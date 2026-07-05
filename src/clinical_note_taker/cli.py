from enum import StrEnum
from pathlib import Path

import anyio
import typer

from .agent import ClinicalNoteAgent
from .config import get_settings
from .models import EncounterInput
from .rendering import render_markdown

app = typer.Typer(
    help="Generate SOAP notes, billing codes, follow-ups, and client instructions "
    "from a veterinary ER encounter transcript."
)


class OutputFormat(StrEnum):
    json = "json"
    markdown = "markdown"


@app.command()
def generate(
    transcript_path: Path = typer.Argument(  # noqa: B008
        ..., help="Path to a text file containing the (ideally PII-scrubbed) transcript."
    ),
    encounter_id: str = typer.Option(..., help="Caller-supplied identifier, not derived from PII."),
    species: str = typer.Option(..., help="e.g. 'canine', 'feline', 'equine'."),
    visit_type: str = typer.Option(None, help="e.g. 'triage', 'critical care follow-up'."),
    output_format: OutputFormat = typer.Option(  # noqa: B008
        OutputFormat.json, "--format", help="Output format."
    ),
) -> None:
    """Generate a clinical note draft from a transcript file."""
    encounter = EncounterInput(
        encounter_id=encounter_id,
        species=species,
        transcript=transcript_path.read_text(),
        visit_type=visit_type,
    )
    agent = ClinicalNoteAgent(get_settings())
    result = anyio.run(agent.generate, encounter)

    if output_format is OutputFormat.markdown:
        typer.echo(render_markdown(result))
    else:
        typer.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
