"""The structured-output tool the model calls to hand back its final draft.

This is the output contract: instead of parsing JSON out of free text (fragile
— markdown fences, commentary, truncation), the model must call this tool
with arguments matching `ClinicalNoteDraft`'s schema. Claude validates the
call's arguments against that schema before it ever reaches our code, and
`agent.py` reads the finished draft straight out of the resulting
`ToolUseBlock.input` — no text parsing involved.

The tool implementation itself is intentionally a no-op beyond acknowledging
receipt; it doesn't need to be stateful, and it isn't the thing that builds
the final ClinicalNoteOutput (agent.py does that, after the SDK session ends).
"""

from typing import Any

from claude_agent_sdk import tool

from ..models import ClinicalNoteDraft

SUBMIT_CLINICAL_NOTE_TOOL_NAME = "submit_clinical_note"


@tool(
    SUBMIT_CLINICAL_NOTE_TOOL_NAME,
    "Submit the completed clinical note draft. Call this exactly once, as your "
    "final action, once the SOAP note, billing codes, follow-up, and client "
    "instructions are all ready.",
    ClinicalNoteDraft.model_json_schema(),
)
async def submit_clinical_note(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": "Note received."}]}


submit_clinical_note_tool = submit_clinical_note
