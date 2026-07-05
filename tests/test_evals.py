import asyncio

from evals.run_evals import load_cases, run_case


def test_at_least_one_eval_case_loads():
    cases = load_cases()
    assert len(cases) >= 1
    assert cases[0].id


def test_eval_case_reports_skipped_until_agent_is_implemented():
    cases = load_cases()
    result = asyncio.run(run_case(cases[0]))
    assert result.status == "skipped"
