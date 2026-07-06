import asyncio

from clinical_note_taker.agent import NoteGenerationError
from evals.run_evals import load_cases, run_case

# Running the eval harness for real (`python -m evals.run_evals`) requires an
# authenticated Claude Code CLI or ANTHROPIC_API_KEY and makes real model
# calls — intentionally not exercised by this file. See run_evals.py.


def test_at_least_one_eval_case_loads():
    cases = load_cases()
    assert len(cases) >= 1
    assert cases[0].id


def test_run_case_reports_fail_when_agent_raises_note_generation_error(monkeypatch):
    async def fake_generate(self, encounter):
        raise NoteGenerationError("model never called submit_clinical_note")

    monkeypatch.setattr(
        "evals.run_evals.ClinicalNoteAgent.generate",
        fake_generate,
    )

    cases = load_cases()
    result = asyncio.run(run_case(cases[0]))
    assert result.status == "fail"
    assert "submit_clinical_note" in result.details[0]
