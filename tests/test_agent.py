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

INVALID_SUBMISSION = {"soap_note": "not a dict"}


def _encounter() -> EncounterInput:
    return EncounterInput(encounter_id="enc-1", species="canine", transcript="...")


def _submission_message(payload: dict[str, object]) -> AssistantMessage:
    return AssistantMessage(
        content=[
            ToolUseBlock(id="1", name="mcp__clinical_tools__submit_clinical_note", input=payload)
        ],
        model="claude",
    )


def _text_message(text: str) -> AssistantMessage:
    return AssistantMessage(content=[TextBlock(text=text)], model="claude")


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
    message = _text_message("working on it...")
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
    message = _submission_message(VALID_SUBMISSION)
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
        _build_output(_encounter(), INVALID_SUBMISSION, requires_clinician_review=True)


class _FakeClient:
    """Stands in for ClaudeSDKClient so generate()'s control flow can be
    tested without a live model call.

    Takes a list of message *batches* — one batch per expected query() call
    (the first for the initial prompt, subsequent ones for each retry
    follow-up). Running out of batches (e.g. more retries than provided)
    yields an empty response, matching a model that goes silent.
    """

    def __init__(self, message_batches: list[list[AssistantMessage]]):
        self._remaining_batches = list(message_batches)
        self._current_batch: list[AssistantMessage] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def query(self, prompt):
        self._current_batch = self._remaining_batches.pop(0) if self._remaining_batches else []

    async def receive_response(self):
        for message in self._current_batch:
            yield message


def _patch_client(monkeypatch, message_batches: list[list[AssistantMessage]]) -> None:
    monkeypatch.setattr(
        agent_module, "ClaudeSDKClient", lambda options: _FakeClient(message_batches)
    )


async def test_generate_raises_after_exhausting_attempts_without_a_submission(monkeypatch):
    _patch_client(monkeypatch, [[_text_message("thinking...")]])

    with pytest.raises(NoteGenerationError):
        await ClinicalNoteAgent(Settings()).generate(_encounter())


async def test_generate_returns_validated_output_on_submission(monkeypatch):
    _patch_client(monkeypatch, [[_submission_message(VALID_SUBMISSION)]])

    output = await ClinicalNoteAgent(Settings()).generate(_encounter())
    assert output.encounter_id == "enc-1"
    assert output.soap_note.assessment == "Suspected gastroenteritis."


async def test_generate_threads_require_clinician_review_setting(monkeypatch):
    _patch_client(monkeypatch, [[_submission_message(VALID_SUBMISSION)]])

    settings = Settings(require_clinician_review=False)
    output = await ClinicalNoteAgent(settings).generate(_encounter())
    assert output.requires_clinician_review is False


async def test_generate_uses_the_latest_of_multiple_submissions_in_one_turn(monkeypatch):
    # Empirically common (see eval runs) — the model revising its own answer
    # mid-turn, not malfunctioning. The last call should win, not error.
    revised_submission = {**VALID_SUBMISSION, "soap_note": {**VALID_SUBMISSION["soap_note"]}}
    revised_submission["soap_note"]["assessment"] = "Revised: suspected pancreatitis."

    _patch_client(
        monkeypatch,
        [[_submission_message(VALID_SUBMISSION), _submission_message(revised_submission)]],
    )

    output = await ClinicalNoteAgent(Settings()).generate(_encounter())
    assert output.soap_note.assessment == "Revised: suspected pancreatitis."


async def test_generate_retries_after_missing_submission_then_succeeds(monkeypatch):
    _patch_client(
        monkeypatch,
        [
            [_text_message("still working...")],
            [_submission_message(VALID_SUBMISSION)],
        ],
    )

    output = await ClinicalNoteAgent(Settings()).generate(_encounter())
    assert output.soap_note.assessment == "Suspected gastroenteritis."


async def test_generate_retries_after_invalid_submission_then_succeeds(monkeypatch):
    _patch_client(
        monkeypatch,
        [
            [_submission_message(INVALID_SUBMISSION)],
            [_submission_message(VALID_SUBMISSION)],
        ],
    )

    output = await ClinicalNoteAgent(Settings()).generate(_encounter())
    assert output.soap_note.assessment == "Suspected gastroenteritis."


async def test_generate_raises_after_exhausting_attempts_on_repeated_invalid_submission(
    monkeypatch,
):
    _patch_client(
        monkeypatch,
        [
            [_submission_message(INVALID_SUBMISSION)],
            [_submission_message(INVALID_SUBMISSION)],
        ],
    )

    with pytest.raises(NoteGenerationError) as exc_info:
        await ClinicalNoteAgent(Settings()).generate(_encounter())
    assert exc_info.value.__cause__ is not None


async def test_generate_chains_the_true_last_error_across_mixed_failure_modes(monkeypatch):
    # Attempt 1 fails with a ValidationError, attempt 2 with a missing
    # submission — the final __cause__ should reflect attempt 2 (the real
    # last failure), not the stale ValidationError from attempt 1.
    _patch_client(
        monkeypatch,
        [
            [_submission_message(INVALID_SUBMISSION)],
            [_text_message("still working...")],
        ],
    )

    with pytest.raises(NoteGenerationError) as exc_info:
        await ClinicalNoteAgent(Settings()).generate(_encounter())
    assert isinstance(exc_info.value.__cause__, NoteGenerationError)
    assert "attempt 2" in str(exc_info.value.__cause__)


async def test_generate_respects_max_submission_attempts_setting(monkeypatch):
    # Only one batch provided; with max_submission_attempts=1 there should be
    # no retry query() call at all, so the second (nonexistent) batch is never
    # needed — confirms the setting actually bounds the loop.
    _patch_client(monkeypatch, [[_text_message("thinking...")]])

    settings = Settings(max_submission_attempts=1)
    with pytest.raises(NoteGenerationError):
        await ClinicalNoteAgent(settings).generate(_encounter())
