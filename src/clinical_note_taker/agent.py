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
see tools/submit_note.py for why.
"""

from __future__ import annotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ToolUseBlock,
    create_sdk_mcp_server,
)

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
    """Raised when the model completes its turn without submitting a note.

    Deliberately not retried here — that's future work (see the "Handle
    malformed or incomplete model output gracefully" issue). For now, a
    missing submission fails loudly rather than returning nothing.
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


def _build_output(encounter: EncounterInput, submission: dict[str, object]) -> ClinicalNoteOutput:
    draft = ClinicalNoteDraft.model_validate(submission)
    return ClinicalNoteOutput(encounter_id=encounter.encounter_id, **draft.model_dump())


class ClinicalNoteAgent:
    """Turns a veterinary ER encounter transcript into a structured note draft."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def generate(self, encounter: EncounterInput) -> ClinicalNoteOutput:
        options = _build_options(self._settings)
        prompt = _build_prompt(encounter)

        submission: dict[str, object] | None = None
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    found = _find_submission(message)
                    if found is not None:
                        submission = found

        if submission is None:
            raise NoteGenerationError(
                f"Model completed its turn without calling {SUBMIT_CLINICAL_NOTE_TOOL_NAME}."
            )

        return _build_output(encounter, submission)
