from typer.testing import CliRunner

from clinical_note_taker import cli as cli_module
from clinical_note_taker.agent import NoteGenerationError
from clinical_note_taker.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "generate" in result.output


def _invoke_generate(tmp_path):
    transcript = tmp_path / "transcript.txt"
    transcript.write_text("Vet: ...")
    return runner.invoke(app, [str(transcript), "--encounter-id", "enc-1", "--species", "canine"])


def test_generate_reports_note_generation_error_cleanly(tmp_path, monkeypatch):
    async def fake_generate(self, encounter):
        raise NoteGenerationError("model never called submit_clinical_note")

    monkeypatch.setattr(cli_module.ClinicalNoteAgent, "generate", fake_generate)

    result = _invoke_generate(tmp_path)
    assert result.exit_code == 1
    assert "Error: model never called submit_clinical_note" in result.output


def test_generate_reports_validation_error_cleanly(tmp_path, monkeypatch):
    async def fake_generate(self, encounter):
        from clinical_note_taker.models import ClinicalNoteDraft

        ClinicalNoteDraft.model_validate({"soap_note": "not a dict"})

    monkeypatch.setattr(cli_module.ClinicalNoteAgent, "generate", fake_generate)

    result = _invoke_generate(tmp_path)
    assert result.exit_code == 1
    assert result.output.startswith("Error:")
