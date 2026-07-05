---
name: soap-note-writer
description: Drafts a Subjective/Objective/Assessment/Plan (SOAP) note from a veterinary ER encounter transcript. Use when asked to produce a clinical note from a clinician-client conversation or raw notes about an animal patient.
---

# SOAP Note Writer

STATUS: scaffold — instructions below are a starting skeleton, not a
finalized clinical documentation standard. Finalize once real (synthetic)
transcripts are available to calibrate against.

Scoped to a veterinary ER for v1. The *patient* is the animal; the *client*
is the owner.

## Goal

Turn a transcript into a well-formed SOAP note:

- **Subjective**: history/complaint as reported by the client, and any
  history in the record (species, breed, age, known conditions).
- **Objective**: observable/measurable findings mentioned in the transcript
  (vitals, exam findings, weight, test results). Vital sign normal ranges
  and drug dosing are species- and weight-dependent — never carry over a
  canine reference range for a feline patient, or vice versa. Do not invent
  findings that were not stated.
- **Assessment**: clinical impression / differential, grounded only in what
  the transcript supports.
- **Plan**: next steps discussed (treatment, medications with weight-based
  dosing where applicable, referrals, tests, follow-up).

## Constraints

- Never fabricate a finding, vital, weight, or history detail that isn't
  present in the transcript. If something is ambiguous, say so rather than
  guessing.
- Keep clinical terminology but avoid unnecessary jargon that obscures
  meaning.
- This output is always a draft pending veterinarian review — do not phrase
  it as final/authoritative.

## TODO before this skill is production-ready

- [ ] Confirm required SOAP sub-sections with the product owner.
- [ ] Decide on handling for multi-problem visits (one SOAP note vs. one
      per problem).
- [ ] Add a few worked examples (input transcript -> expected note) using
      synthetic vet ER transcripts.
