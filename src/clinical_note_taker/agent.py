"""Agent orchestration built on the Claude Agent SDK.

Scoped to a veterinary ER for v1 (see models.py). Generalizing to other
species/specialties is a deliberate follow-up, not built here.

Security/privacy note: the agent disables the SDK's default built-in
toolset (`tools=[]`) — this process has no business running Bash or
touching arbitrary files on disk. It's only given the specific in-process
tools it needs (SNOMED CT lookup, client PII redaction, note submission)
plus its skills.

Output contract: the model doesn't return its answer as free text. It must
call the `submit_clinical_note` tool exactly once, as its final action, with
arguments matching `ClinicalNoteDraft`. We read the finished draft straight
out of that tool call's arguments rather than parsing JSON out of prose —
see tools/submit_note.py for why. A missing or schema-invalid submission is
retried, feeding the specific error back to the model, up to
`Settings.max_submission_attempts` times before failing.
"""

from __future__ import annotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ToolUseBlock,
    create_sdk_mcp_server,
)
from pydantic import ValidationError

from .config import AGENT_WORKSPACE, Settings, get_settings
from .models import ClinicalNoteDraft, ClinicalNoteOutput, EncounterInput
from .tools import (
    SUBMIT_CLINICAL_NOTE_TOOL_NAME,
    pii_redaction_tool,
    snomed_lookup_tool,
    submit_clinical_note_tool,
)

SKILL_NAMES = ["soap-note-writer", "medical-billing-coder", "client-instructions-writer"]

_MCP_SERVER_NAME = "clinical_tools"
_SUBMIT_TOOL_FULL_NAME = f"mcp__{_MCP_SERVER_NAME}__{SUBMIT_CLINICAL_NOTE_TOOL_NAME}"

SYSTEM_PROMPT = f"""You are a clinical documentation assistant for a veterinary emergency room.
You draft SOAP notes, suggest SNOMED CT (veterinary extension) diagnosis codes, propose
follow-up actions, and write plain-language instructions for the client (the animal's owner)
from an encounter transcript. You never fabricate findings, vitals, or history details that
are not supported by the transcript, and you always flag your output as a draft that requires
review by a licensed veterinarian. Use the snomed_lookup tool rather than recalling codes from
memory, and never invent a numeric concept ID yourself.

Once the SOAP note, billing codes, follow-up, and client instructions are all ready, call the
{SUBMIT_CLINICAL_NOTE_TOOL_NAME} tool exactly once, as your final action, with the complete
draft. Do not describe the note in your own text response — the tool call is the deliverable."""


class NoteGenerationError(RuntimeError):
    """Raised when the model fails to produce a valid note.

    A missing or schema-invalid submission is retried up to
    `Settings.max_submission_attempts` times, feeding the specific error
    back to the model, before this is raised for good.
    """


def _build_options(settings: Settings) -> ClaudeAgentOptions:
    tools_server = create_sdk_mcp_server(
        name=_MCP_SERVER_NAME,
        version="0.1.0",
        tools=[snomed_lookup_tool, pii_redaction_tool, submit_clinical_note_tool],
    )
    return ClaudeAgentOptions(
        tools=[],
        mcp_servers={_MCP_SERVER_NAME: tools_server},
        allowed_tools=[
            f"mcp__{_MCP_SERVER_NAME}__snomed_lookup",
            f"mcp__{_MCP_SERVER_NAME}__pii_redaction",
            _SUBMIT_TOOL_FULL_NAME,
        ],
        skills=SKILL_NAMES,
        system_prompt=SYSTEM_PROMPT,
        cwd=str(AGENT_WORKSPACE),
        setting_sources=["project"],
        model=settings.anthropic_model,
        max_turns=settings.max_turns,
        permission_mode="default",
    )


def _build_prompt(encounter: EncounterInput) -> str:
    return (
        "Draft a clinical note for the following veterinary ER encounter transcript. "
        "Use the soap-note-writer, medical-billing-coder, and client-instructions-writer "
        "skills as appropriate.\n\n"
        f"Encounter ID: {encounter.encounter_id}\n"
        f"Species: {encounter.species}\n"
        f"Visit type: {encounter.visit_type or 'unspecified'}\n\n"
        f"Transcript:\n{encounter.transcript}"
    )


def _find_submission(message: AssistantMessage) -> dict[str, object] | None:
    for block in message.content:
        if isinstance(block, ToolUseBlock) and block.name == _SUBMIT_TOOL_FULL_NAME:
            return block.input
    return None


async def _collect_submission(client: ClaudeSDKClient) -> dict[str, object] | None:
    """Drain one turn's worth of messages, returning the submitted draft, if any.

    If the model calls `submit_clinical_note` more than once in the same
    turn, the *last* call wins. Empirically (see eval runs) this is common —
    the model revising its own answer mid-turn rather than malfunctioning —
    so it's treated the same as a human re-submitting a form, not an error.
    """
    submission: dict[str, object] | None = None
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            found = _find_submission(message)
            if found is not None:
                submission = found
    return submission


def _build_output(
    encounter: EncounterInput, submission: dict[str, object], *, requires_clinician_review: bool
) -> ClinicalNoteOutput:
    draft = ClinicalNoteDraft.model_validate(submission)
    return ClinicalNoteOutput(
        encounter_id=encounter.encounter_id,
        requires_clinician_review=requires_clinician_review,
        **draft.model_dump(),
    )


class ClinicalNoteAgent:
    """Turns a veterinary ER encounter transcript into a structured note draft."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def generate(self, encounter: EncounterInput) -> ClinicalNoteOutput:
        options = _build_options(self._settings)
        prompt = _build_prompt(encounter)
        max_attempts = self._settings.max_submission_attempts

        last_error: Exception = NoteGenerationError(
            f"Model completed its turn without calling {SUBMIT_CLINICAL_NOTE_TOOL_NAME}."
        )

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)

            for attempt in range(1, max_attempts + 1):
                submission = await _collect_submission(client)

                if submission is not None:
                    try:
                        return _build_output(
                            encounter,
                            submission,
                            requires_clinician_review=self._settings.require_clinician_review,
                        )
                    except ValidationError as exc:
                        last_error = exc
                        feedback = (
                            f"Your {SUBMIT_CLINICAL_NOTE_TOOL_NAME} call was invalid: {exc} "
                            "Call it again with corrected arguments."
                        )
                else:
                    last_error = NoteGenerationError(
                        f"Model didn't call {SUBMIT_CLINICAL_NOTE_TOOL_NAME} on attempt {attempt}."
                    )
                    feedback = (
                        f"You didn't call {SUBMIT_CLINICAL_NOTE_TOOL_NAME}. Call it now with "
                        "the complete draft."
                    )

                if attempt < max_attempts:
                    await client.query(feedback)

        raise NoteGenerationError(
            f"Model failed to submit a valid note after {max_attempts} attempt(s)."
        ) from last_error
