from clinical_note_taker.models import (
    BillingCode,
    ClientInstructions,
    ClinicalNoteOutput,
    CodeSystem,
    FollowUpSuggestion,
    SoapNote,
)
from clinical_note_taker.rendering import render_markdown


def _sample_output() -> ClinicalNoteOutput:
    return ClinicalNoteOutput(
        encounter_id="enc-1",
        soap_note=SoapNote(
            subjective="Owner reports vomiting since this morning.",
            objective="HR 120, T 102.1F, mild abdominal discomfort on palpation.",
            assessment="Suspected gastroenteritis.",
            plan="Start supportive care, recheck in 48 hours.",
        ),
        billing_codes=[
            BillingCode(
                system=CodeSystem.SNOMED_CT,
                code="unknown",
                description="Gastroenteritis",
                confidence=0.6,
            )
        ],
        follow_up=[FollowUpSuggestion(recommendation="Recheck", timeframe="48 hours")],
        client_instructions=ClientInstructions(
            summary="Keep him on a bland diet for a few days.",
            action_items=["Offer small amounts of water frequently"],
            warning_signs=["Repeated vomiting", "Lethargy"],
        ),
    )


def test_render_markdown_includes_all_sections():
    markdown = render_markdown(_sample_output())
    assert "# Encounter Note — enc-1" in markdown
    assert "## Subjective" in markdown
    assert "## Billing Codes" in markdown
    assert "## Follow-Up" in markdown
    assert "## Instructions for the Client" in markdown
    assert "Repeated vomiting" in markdown
