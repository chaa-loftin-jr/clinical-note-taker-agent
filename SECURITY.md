# Security & Privacy

This project is scoped to a veterinary ER. **HIPAA does not apply here** —
HIPAA protects human patient health information, and animals aren't
"individuals" under the statute. There's also no veterinary equivalent of
ICD-10-CM/CPT (see `src/clinical_note_taker/tools/snomed_lookup.py`). What
still applies is ordinary data-privacy hygiene around the *client* (the
animal's owner): their name, contact info, and payment details are regular
PII, and encounter transcripts/notes are still sensitive business data
worth protecting carefully. Treat the guidance below as a baseline, not a
substitute for a privacy/compliance review by whoever owns that at your
organization — especially if this is ever extended to a human-medicine
domain profile, where HIPAA obligations would apply.

## Handling client & patient data

- Never commit real transcripts, sample data, or output notes to this
  repository, issues, or pull requests — including in screenshots or logs
  pasted into a GitHub comment.
- The agent disables all general-purpose file/shell tools (see
  `src/clinical_note_taker/agent.py`) and only exposes the specific tools it
  needs, to limit what a compromised or misbehaving model turn could do.
- `src/clinical_note_taker/tools/pii_redaction.py` provides best-effort
  scrubbing of client PII for logs/telemetry. It is defense-in-depth, not a
  de-identification guarantee.
- All generated output is flagged as a draft requiring veterinarian review
  (`ClinicalNoteOutput.requires_clinician_review`) — it is not intended to
  enter the medical record or a billing workflow unreviewed.
- SNOMED CT concept IDs returned by `snomed_lookup` are explicitly marked
  unverified until checked against an authoritative source — don't strip
  that caveat out downstream.

## Reporting a vulnerability

If you find a security issue, please report it privately rather than opening
a public issue. Open a GitHub issue asking for a private contact channel, or
reach out to the repository owner directly.
