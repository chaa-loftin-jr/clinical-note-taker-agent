import clinical_note_taker


def test_package_exposes_version() -> None:
    assert isinstance(clinical_note_taker.__version__, str)
    assert clinical_note_taker.__version__
