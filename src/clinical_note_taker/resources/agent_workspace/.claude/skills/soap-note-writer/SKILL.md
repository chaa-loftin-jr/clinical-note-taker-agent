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

## Worked examples

Both drawn from real (synthetic) model runs — see `evals/cases/canine_gdv_er.yaml`
for the full transcript behind example 1.

### Example 1: canine, suspected GDV

Transcript excerpt: owner reports sudden abdominal distension and nonproductive
retching after dinner; exam finds a tympanic abdomen and tachycardia (HR 160).

Expected SOAP note:

- **Subjective**: "Owner reports that the dog's abdomen appeared distended
  approximately 1 hour ago, beginning shortly after dinner. Dog has been
  retching repeatedly with nothing produced (nonproductive retching). Owner
  describes the dog as very restless and unwilling to lie down."
- **Objective**: "On physical exam, abdomen is tympanic on palpation. Heart
  rate elevated at 160 bpm (tachycardic). No other vital signs, temperature,
  mucous membrane color, or capillary refill time were reported in this
  encounter." — note what's *absent* is stated explicitly rather than filled in.
- **Assessment**: "...highly concerning for gastric dilatation-volvulus (GDV),
  a life-threatening emergency. Diagnosis is presumptive pending radiographic
  confirmation" — hedged, not asserted as fact.
- **Plan**: numbered, concrete next steps (radiographs, IV fluids, monitoring,
  contingent surgery, owner communication) — grounded in what the transcript's
  clinician actually said.

### Example 2: feline, suspected urethral obstruction

Transcript excerpt: owner reports a cat straining in the litter box since the
previous evening with minimal output and vocalizing in pain; exam finds a
firm, distended, painful bladder.

Expected SOAP note (excerpt):

- **Objective**: "...bladder is firm, markedly distended, and painful on
  palpation. No other objective findings (e.g., vital signs, mucous membrane
  color, heart rate/rhythm, temperature) were recorded in the transcript."
- **Assessment**: "Clinical suspicion for feline urethral obstruction given
  history of stranguria... Diagnosis is presumptive pending confirmatory
  bloodwork; this is an emergent, potentially life-threatening condition."

Both examples show the pattern to match: state findings plainly, hedge
differentials appropriately, and say explicitly when something wasn't
reported rather than inferring it.

## TODO before this skill is production-ready

- [x] Add a few worked examples (input transcript -> expected note) using
      synthetic vet ER transcripts.
- [ ] Confirm required SOAP sub-sections with the product owner.
- [ ] Decide on handling for multi-problem visits (one SOAP note vs. one
      per problem).
