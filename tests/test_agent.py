"""Unit tests for the agent's option wiring.

These deliberately avoid calling ClinicalNoteAgent.generate() end-to-end: that
spawns the bundled Claude Code CLI and requires real credentials/network,
which isn't appropriate for the unit test suite.
"""

from clinical_note_taker.agent import SKILL_NAMES, _build_options
from clinical_note_taker.config import Settings


def test_build_options_disables_builtin_tools():
    options = _build_options(Settings())
    assert options.tools == []


def test_build_options_only_allows_domain_tools():
    options = _build_options(Settings())
    assert set(options.allowed_tools) == {
        "mcp__clinical_tools__snomed_lookup",
        "mcp__clinical_tools__pii_redaction",
    }


def test_build_options_enables_expected_skills():
    options = _build_options(Settings())
    assert options.skills == SKILL_NAMES
