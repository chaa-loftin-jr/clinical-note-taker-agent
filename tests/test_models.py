import pytest
from pydantic import ValidationError

from clinical_note_taker.models import (
    ClientInstructions,
    ClinicalNoteOutput,
    EncounterInput,
    FollowUpSuggestion,
    SoapNote,
)


def test_encounter_input_requires_transcript():
    with pytest.raises(ValidationError):
        EncounterInput(encounter_id="enc-1", species="canine")  # type: ignore[call-arg]


def test_encounter_input_minimal():
    encounter = EncounterInput(
        encounter_id="enc-1", species="canine", transcript="patient reports..."
    )
    assert encounter.visit_type is None


def test_clinical_note_output_defaults_to_requiring_review():
    output = ClinicalNoteOutput(
        encounter_id="enc-1",
        soap_note=SoapNote(subjective="", objective="", assessment="", plan=""),
        client_instructions=ClientInstructions(summary="Keep him quiet tonight."),
        follow_up=[FollowUpSuggestion(recommendation="Recheck in 2 weeks")],
    )
    assert output.requires_clinician_review is True
    assert "review" in output.disclaimer.lower()
