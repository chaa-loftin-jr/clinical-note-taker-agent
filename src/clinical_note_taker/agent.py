"""Agent orchestration built on the Claude Agent SDK.

Scoped to a veterinary ER for v1 (see models.py). Generalizing to other
species/specialties is a deliberate follow-up, not built here.

Security/privacy note: the agent disables the SDK's default built-in
toolset (`tools=[]`) — this process has no business running Bash or
touching arbitrary files on disk. It's only given the specific in-process
tools it needs (SNOMED CT lookup, client PII redaction) plus its skills.
"""

from __future__ import annotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    create_sdk_mcp_server,
)

from .config import AGENT_WORKSPACE, Settings, get_settings
from .models import ClinicalNoteOutput, EncounterInput
from .tools import pii_redaction_tool, snomed_lookup_tool

SKILL_NAMES = ["soap-note-writer", "medical-billing-coder", "client-instructions-writer"]

SYSTEM_PROMPT = """You are a clinical documentation assistant for a veterinary emergency room.
You draft SOAP notes, suggest SNOMED CT (veterinary extension) diagnosis codes, propose
follow-up actions, and write plain-language instructions for the client (the animal's owner)
from an encounter transcript. You never fabricate findings, vitals, or history details that
are not supported by the transcript, and you always flag your output as a draft that requires
review by a licensed veterinarian. Use the snomed_lookup tool rather than recalling codes from
memory, and never invent a numeric concept ID yourself."""


def _build_options(settings: Settings) -> ClaudeAgentOptions:
    tools_server = create_sdk_mcp_server(
        name="clinical_tools",
        version="0.1.0",
        tools=[snomed_lookup_tool, pii_redaction_tool],
    )
    return ClaudeAgentOptions(
        tools=[],
        mcp_servers={"clinical_tools": tools_server},
        allowed_tools=[
            "mcp__clinical_tools__snomed_lookup",
            "mcp__clinical_tools__pii_redaction",
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


class ClinicalNoteAgent:
    """Turns a veterinary ER encounter transcript into a structured note draft.

    v1 scaffold: orchestration wiring (options/tools/skills) is real and
    testable; the prompting strategy and output-parsing contract are not
    implemented yet, pending calibration against real (synthetic) transcripts.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def generate(self, encounter: EncounterInput) -> ClinicalNoteOutput:
        options = _build_options(self._settings)
        prompt = _build_prompt(encounter)

        raw_text = ""
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            raw_text += block.text

        raise NotImplementedError(
            "Output parsing into ClinicalNoteOutput is not implemented yet — the "
            "SOAP/billing/instructions skills need a defined output contract first. "
            f"Raw model response was:\n{raw_text}"
        )
