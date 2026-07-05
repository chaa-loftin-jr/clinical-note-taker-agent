"""Structured input/output schemas for the clinical note-taker agent.

Scoped to a veterinary ER for v1. Note the vet-specific terminology: the
*patient* is the animal, the *client* is the owner — after-visit instructions
go to the client, not the patient. Generalizing to other species/specialties
(and to human medicine) is intentionally deferred to a follow-up PR.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class EncounterInput(BaseModel):
    """A single veterinary ER encounter to summarize.

    `transcript` is expected to already be scrubbed of client (owner) PII
    upstream where possible; the agent additionally applies its own PII
    redaction pass (see tools/pii_redaction.py) before anything is logged.
    """

    encounter_id: str = Field(..., description="Caller-supplied identifier, not derived from PII.")
    species: str = Field(..., description="Patient species, e.g. 'canine', 'feline', 'equine'.")
    transcript: str = Field(..., description="Raw transcript or clinician's raw notes.")
    visit_type: str | None = Field(
        default=None, description="e.g. 'triage', 'critical care follow-up'."
    )


class CodeSystem(StrEnum):
    """Coding system used for billing_codes.

    Only SNOMED CT (veterinary extension) for now — see tools/snomed_lookup.py.
    ICD-10-CM/CPT are human-medicine code sets that don't apply here; they'd
    be reintroduced under a human-medicine domain profile in a future PR.
    """

    SNOMED_CT = "SNOMED-CT"


class BillingCode(BaseModel):
    system: CodeSystem
    code: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)


class SoapNote(BaseModel):
    subjective: str
    objective: str
    assessment: str
    plan: str


class FollowUpSuggestion(BaseModel):
    recommendation: str
    timeframe: str | None = None
    rationale: str | None = None


class ClientInstructions(BaseModel):
    """After-visit instructions for the client (the animal's owner)."""

    summary: str
    action_items: list[str] = Field(default_factory=list)
    warning_signs: list[str] = Field(default_factory=list)


class ClinicalNoteOutput(BaseModel):
    encounter_id: str
    soap_note: SoapNote
    billing_codes: list[BillingCode] = Field(default_factory=list)
    follow_up: list[FollowUpSuggestion] = Field(default_factory=list)
    client_instructions: ClientInstructions
    requires_clinician_review: bool = Field(
        default=True,
        description="Always true until a licensed veterinarian has reviewed and signed off.",
    )
    disclaimer: str = Field(
        default=(
            "AI-generated draft. Not a substitute for professional veterinary "
            "judgment. Must be reviewed and signed off by a licensed "
            "veterinarian before use in the patient's medical record or for "
            "billing."
        )
    )
