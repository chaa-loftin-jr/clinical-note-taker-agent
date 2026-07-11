"""Eval harness entry point.

Usage:
    python -m evals.run_evals

For each case under evals/cases/*.yaml, runs the agent for real (requires an
authenticated Claude Code CLI or ANTHROPIC_API_KEY) and checks the output
against the case's deterministic assertions.

An LLM-as-judge pass for subjective qualities (completeness, tone) is a
planned fast-follow, layered on top of these deterministic checks rather
than replacing them — see evals/schema.py.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from clinical_note_taker.agent import ClinicalNoteAgent, NoteGenerationError
from clinical_note_taker.models import ClinicalNoteOutput, EncounterInput

from .schema import EvalCase

CASES_DIR = Path(__file__).parent / "cases"


@dataclass
class EvalResult:
    case_id: str
    status: str  # "pass" | "fail" | "skipped"
    details: list[str]


def load_cases() -> list[EvalCase]:
    cases = []
    for path in sorted(CASES_DIR.glob("*.yaml")):
        cases.append(EvalCase.model_validate(yaml.safe_load(path.read_text())))
    return cases


def check_output(case: EvalCase, output: ClinicalNoteOutput) -> list[str]:
    failures = []

    assessment_text = output.soap_note.assessment.lower()
    for keyword in case.must_include_assessment_keywords:
        if keyword.lower() not in assessment_text:
            failures.append(f"assessment missing keyword {keyword!r}")

    codes = {bc.code for bc in output.billing_codes}
    for expected in case.must_include_diagnosis_codes:
        if expected not in codes:
            failures.append(f"missing expected diagnosis code {expected!r}")

    instructions_text = " ".join(
        [
            output.client_instructions.summary,
            *output.client_instructions.action_items,
            *output.client_instructions.warning_signs,
        ]
    ).lower()
    for keyword in case.must_include_instruction_keywords:
        if keyword.lower() not in instructions_text:
            failures.append(f"client instructions missing keyword {keyword!r}")

    full_text = output.model_dump_json().lower()
    for phrase in case.forbidden_phrases:
        if phrase.lower() in full_text:
            failures.append(f"output contains forbidden phrase {phrase!r}")

    return failures


async def run_case(case: EvalCase) -> EvalResult:
    encounter = EncounterInput(
        encounter_id=case.id,
        species=case.species,
        transcript=case.transcript,
        visit_type=case.visit_type,
    )
    try:
        output = await ClinicalNoteAgent().generate(encounter)
    except NoteGenerationError as exc:
        return EvalResult(case.id, "fail", [str(exc)])

    failures = check_output(case, output)
    return EvalResult(case.id, "fail" if failures else "pass", failures)


async def main() -> int:
    results = [await run_case(case) for case in load_cases()]

    for result in results:
        print(f"[{result.status.upper():7}] {result.case_id}")
        for detail in result.details:
            print(f"          - {detail}")

    return 1 if any(r.status == "fail" for r in results) else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
