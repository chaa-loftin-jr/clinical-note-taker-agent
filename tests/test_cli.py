from typer.testing import CliRunner

from clinical_note_taker.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "generate" in result.output
