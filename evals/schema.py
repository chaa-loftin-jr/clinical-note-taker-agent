"""Schema for golden eval cases.

Each case is a synthetic (never real-client/patient) transcript paired with
deterministic checks the generated note must satisfy. This is intentionally
rubric-light for the scaffold — an LLM-as-judge pass for subjective qualities
(completeness, tone) is a planned fast-follow once there's real agent output
to calibrate a rubric against.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvalCase(BaseModel):
    id: str
    description: str
    species: str
    transcript: str
    visit_type: str | None = None

    # Deterministic checks against the generated ClinicalNoteOutput.
    must_include_diagnosis_codes: list[str] = Field(default_factory=list)
    must_include_instruction_keywords: list[str] = Field(default_factory=list)
    forbidden_phrases: list[str] = Field(
        default_factory=list,
        description="Phrases that must never appear (e.g. an unstated medication).",
    )
