from clinical_note_taker.config import get_settings


def test_defaults(monkeypatch):
    monkeypatch.delenv("CNT_ANTHROPIC_MODEL", raising=False)
    settings = get_settings()
    assert settings.redact_pii_in_logs is True
    assert settings.require_clinician_review is True
    assert settings.max_turns > 0


def test_env_override(monkeypatch):
    monkeypatch.setenv("CNT_MAX_TURNS", "3")
    settings = get_settings()
    assert settings.max_turns == 3
