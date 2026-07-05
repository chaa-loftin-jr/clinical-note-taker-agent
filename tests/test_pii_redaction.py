from clinical_note_taker.tools.pii_redaction import redact


def test_redacts_ssn():
    assert "123-45-6789" not in redact("SSN: 123-45-6789")


def test_redacts_phone():
    assert "555-123-4567" not in redact("Call 555-123-4567")


def test_redacts_date():
    assert "3/4/2026" not in redact("Seen on 3/4/2026")


def test_redacts_record_id():
    assert "MRN: 12345" not in redact("MRN: 12345")
    assert "Case #98765" not in redact("Case #98765")


def test_leaves_clinical_text_alone():
    text = "Patient is a 4-year-old canine presenting with mild lethargy."
    assert redact(text) == text
