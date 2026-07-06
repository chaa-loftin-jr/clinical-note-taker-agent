"""Unit tests for the agent's option wiring and output extraction.

These deliberately avoid calling ClinicalNoteAgent.generate() end-to-end: that
spawns the bundled Claude Code CLI and requires real credentials/network,
which isn't appropriate for the unit test suite. The extraction/validation
logic (_find_submission, _build_output) is a pure function of SDK message
objects, so it's tested directly without a live model.
"""

import pytest
from claude_agent_sdk import AssistantMessage, TextBlock, ToolUseBlock

from clinical_note_taker import agent as agent_module
from clinical_note_taker.agent import (
    SKILL_NAMES,
    ClinicalNoteAgent,
    NoteGenerationError,
    _build_options,
    _build_output,
    _find_submission,
)
from clinical_note_taker.config import Settings
from clinical_note_taker.models import EncounterInput

VALID_SUBMISSION = {
    "soap_note": {
        "subjective": "Vomiting since this morning.",
        "objective": "HR 120, T 102.1F.",
        "assessment": "Suspected gastroenteritis.",
        "plan": "Supportive care, recheck in 48 hours.",
    },
    "billing_codes": [],
    "follow_up": [{"recommendation": "Recheck", "timeframe": "48 hours"}],
    "client_instructions": {
        "summary": "Keep him on a bland diet for a few days.",
        "action_items": ["Offer small amounts of water frequently"],
        "warning_signs": ["Repeated vomiting", "Lethargy"],
    },
}


def _encounter() -> EncounterInput:
    return EncounterInput(encounter_id="enc-1", species="canine", transcript="...")


def test_build_options_disables_builtin_tools():
    options = _build_options(Settings())
    assert options.tools == []


def test_build_options_only_allows_domain_tools():
    options = _build_options(Settings())
    assert set(options.allowed_tools) == {
        "mcp__clinical_tools__snomed_lookup",
        "mcp__clinical_tools__pii_redaction",
        "mcp__clinical_tools__submit_clinical_note",
    }


def test_build_options_enables_expected_skills():
    options = _build_options(Settings())
    assert options.skills == SKILL_NAMES


def test_find_submission_returns_none_when_absent():
    message = AssistantMessage(content=[TextBlock(text="working on it...")], model="claude")
    assert _find_submission(message) is None


def test_find_submission_ignores_other_tool_calls():
    message = AssistantMessage(
        content=[
            ToolUseBlock(id="1", name="mcp__clinical_tools__snomed_lookup", input={"query": "gdv"})
        ],
        model="claude",
    )
    assert _find_submission(message) is None


def test_find_submission_extracts_matching_tool_call():
    message = AssistantMessage(
        content=[
            ToolUseBlock(
                id="1", name="mcp__clinical_tools__submit_clinical_note", input=VALID_SUBMISSION
            )
        ],
        model="claude",
    )
    assert _find_submission(message) == VALID_SUBMISSION


def test_build_output_merges_encounter_id_with_draft():
    output = _build_output(_encounter(), VALID_SUBMISSION, requires_clinician_review=True)
    assert output.encounter_id == "enc-1"
    assert output.soap_note.assessment == "Suspected gastroenteritis."
    assert output.requires_clinician_review is True


def test_build_output_respects_requires_clinician_review_false():
    output = _build_output(_encounter(), VALID_SUBMISSION, requires_clinician_review=False)
    assert output.requires_clinician_review is False


def test_build_output_rejects_invalid_submission():
    with pytest.raises(ValueError):
        _build_output(_encounter(), {"soap_note": "not a dict"}, requires_clinician_review=True)


class _FakeClient:
    """Stands in for ClaudeSDKClient so generate()'s control flow can be
    tested without a live model call."""

    def __init__(self, messages):
        self._messages = messages

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def query(self, prompt):
        pass

    async def receive_response(self):
        for message in self._messages:
            yield message


async def test_generate_raises_without_a_submission(monkeypatch):
    no_submission = [AssistantMessage(content=[TextBlock(text="thinking...")], model="claude")]
    monkeypatch.setattr(agent_module, "ClaudeSDKClient", lambda options: _FakeClient(no_submission))

    with pytest.raises(NoteGenerationError):
        await ClinicalNoteAgent(Settings()).generate(_encounter())


async def test_generate_returns_validated_output_on_submission(monkeypatch):
    messages = [
        AssistantMessage(
            content=[
                ToolUseBlock(
                    id="1",
                    name="mcp__clinical_tools__submit_clinical_note",
                    input=VALID_SUBMISSION,
                )
            ],
            model="claude",
        )
    ]
    monkeypatch.setattr(agent_module, "ClaudeSDKClient", lambda options: _FakeClient(messages))

    output = await ClinicalNoteAgent(Settings()).generate(_encounter())
    assert output.encounter_id == "enc-1"
    assert output.soap_note.assessment == "Suspected gastroenteritis."


async def test_generate_threads_require_clinician_review_setting(monkeypatch):
    messages = [
        AssistantMessage(
            content=[
                ToolUseBlock(
                    id="1",
                    name="mcp__clinical_tools__submit_clinical_note",
                    input=VALID_SUBMISSION,
                )
            ],
            model="claude",
        )
    ]
    monkeypatch.setattr(agent_module, "ClaudeSDKClient", lambda options: _FakeClient(messages))

    settings = Settings(require_clinician_review=False)
    output = await ClinicalNoteAgent(settings).generate(_encounter())
    assert output.requires_clinician_review is False


async def test_generate_raises_on_duplicate_submission(monkeypatch):
    submit_message = AssistantMessage(
        content=[
            ToolUseBlock(
                id="1",
                name="mcp__clinical_tools__submit_clinical_note",
                input=VALID_SUBMISSION,
            )
        ],
        model="claude",
    )
    monkeypatch.setattr(
        agent_module,
        "ClaudeSDKClient",
        lambda options: _FakeClient([submit_message, submit_message]),
    )

    with pytest.raises(NoteGenerationError):
        await ClinicalNoteAgent(Settings()).generate(_encounter())
