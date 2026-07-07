---
name: medical-billing-coder
description: Suggests candidate SNOMED CT (veterinary extension) diagnosis codes for an encounter, using the snomed_lookup tool. Use after a SOAP note has been drafted.
---

# Medical Billing Coder

STATUS: scaffold. Veterinary medicine has no equivalent of ICD-10-CM/CPT —
those are human-medicine billing code sets tied to CMS/insurance claims that
vet practices don't submit to. SNOMED CT's veterinary extension is the
closest real, standardized fit for diagnosis coding, but the `snomed_lookup`
tool this skill depends on currently returns **unverified** concept IDs from
a small hand-picked starter table (see src/clinical_note_taker/tools/snomed_lookup.py).
Do not use this skill's output for anything beyond a demo until those codes
are verified against the VTSL browser or replaced by a live terminology
server / API integration (tracked follow-up task).

## Goal

Given the assessment from a SOAP note, suggest SNOMED CT (veterinary
extension) terms via the `snomed_lookup` tool for each distinct clinical
finding/diagnosis. Each suggestion must include:

- the term and concept ID returned by the tool (verbatim, including its
  verified/unverified status),
- a confidence score,
- a short justification tying it back to specific transcript content.

## Constraints

- Always call `snomed_lookup` rather than recalling a code from memory —
  model-recalled codes are error-prone, and this output may eventually feed
  real billing/record-keeping decisions.
- If the tool returns no match, say so explicitly rather than guessing a
  code, and never invent a numeric concept ID yourself.
- Always surface the tool's unverified/verified status alongside any code —
  don't strip that caveat out of the final output.

## Worked examples

Both drawn from real (synthetic) model runs, and chosen to show both branches
of the "no match" constraint above.

### Example 1: snomed_lookup finds a candidate term

Assessment: suspected gastric dilatation-volvulus (GDV) in a dog.

`snomed_lookup("gdv")` returns: *"Gastric dilation-volvulus of dog
(concept_id=unknown). UNVERIFIED concept ID — do not use for real coding
until checked against the VTSL SNOMED CT veterinary extension browser."*

Expected billing code entry — the caveat is carried through, not dropped:

> **SNOMED-CT UNVERIFIED** — Gastric dilation-volvulus of dog
> (suspected/presumptive) — lookup tool returned this candidate term but no
> valid concept ID; requires verification against the official VTSL SNOMED
> CT veterinary extension browser before use in billing or records.
> Diagnosis not yet radiographically confirmed at time of note. (confidence: 25%)

### Example 2: snomed_lookup finds no match

Assessment: suspected feline urethral obstruction with possible secondary
hyperkalemia. None of `snomed_lookup`'s starter-table terms match "urethral
obstruction," "stranguria," "bladder distension," or "hyperkalemia."

Expected behavior — no code is fabricated; the finding is reported in plain
language and explicitly left uncoded:

> Note: No matching SNOMED CT (veterinary extension) concept was found in
> the local lookup table for urethral obstruction, stranguria, bladder
> distension, or hyperkalemia; these findings are reported here in plain
> language and left uncoded rather than assigning an unverified code.

## TODO before this skill is production-ready

- [ ] Verify (or replace) the starter table's concept IDs against the VTSL
      SNOMED CT veterinary extension browser, or wire up a live lookup.
- [ ] Define the confidence threshold below which a code should be omitted
      instead of suggested.
- [ ] Add eval cases with known-correct terms for common ER presentations.
