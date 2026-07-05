"""Best-effort PII redaction used before anything is logged or persisted.

This scrubs personally identifying information about the client (the animal's
owner) — not "PHI" in the HIPAA sense, since HIPAA doesn't apply to
veterinary patients. Regex-based redaction alone is not a de-identification
guarantee — treat this as defense-in-depth for logs/telemetry, and have
whoever owns privacy/compliance for this project review it before it's
trusted with real transcripts.
"""

import re
from typing import Any

from claude_agent_sdk import tool

_PATTERNS: dict[str, re.Pattern[str]] = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "date": re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),
    "record_id": re.compile(
        r"\b(?:MRN|Case\s*#|Patient\s*ID|Client\s*ID)[:\s]*\d+\b", re.IGNORECASE
    ),
}


def redact(text: str) -> str:
    redacted = text
    for label, pattern in _PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{label.upper()}]", redacted)
    return redacted


@tool(
    "pii_redaction", "Redact likely client PII from a block of text before logging.", {"text": str}
)
async def pii_redaction(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": redact(args["text"])}]}


pii_redaction_tool = pii_redaction
