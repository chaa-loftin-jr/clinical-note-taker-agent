"""Deterministic Markdown rendering of a ClinicalNoteOutput.

Kept as a pure function of the structured output: the model only ever has
to produce one artifact (the JSON matching ClinicalNoteOutput), and this
human-readable view is derived from it rather than generated separately —
so it can't drift from the structured data and costs no extra model call.
"""

from __future__ import annotations

from .models import ClinicalNoteOutput


def render_markdown(output: ClinicalNoteOutput) -> str:
    lines = [
        f"# Encounter Note — {output.encounter_id}",
        "",
        f"> {output.disclaimer}",
        "",
        "## Subjective",
        output.soap_note.subjective,
        "",
        "## Objective",
        output.soap_note.objective,
        "",
        "## Assessment",
        output.soap_note.assessment,
        "",
        "## Plan",
        output.soap_note.plan,
    ]

    if output.billing_codes:
        lines += ["", "## Billing Codes"]
        lines += [
            f"- **{code.system.value} {code.code}** — {code.description} "
            f"(confidence: {code.confidence:.0%})"
            for code in output.billing_codes
        ]

    if output.follow_up:
        lines += ["", "## Follow-Up"]
        lines += [
            f"- {item.recommendation}" + (f" ({item.timeframe})" if item.timeframe else "")
            for item in output.follow_up
        ]

    lines += ["", "## Instructions for the Client", output.client_instructions.summary]

    if output.client_instructions.action_items:
        lines += ["", "**What to do:**"]
        lines += [f"- {item}" for item in output.client_instructions.action_items]

    if output.client_instructions.warning_signs:
        lines += ["", "**Seek urgent care if you notice:**"]
        lines += [f"- {item}" for item in output.client_instructions.warning_signs]

    return "\n".join(lines)
