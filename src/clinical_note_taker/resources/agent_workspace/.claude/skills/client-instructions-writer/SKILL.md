---
name: client-instructions-writer
description: Writes plain-language, client-facing instructions and follow-up guidance from a SOAP note. Use to produce the after-visit summary given to the animal's owner.
---

# Client Instructions Writer

STATUS: scaffold — instructions below are a starting skeleton, to be
finalized against a target reading level and any organizational
after-visit-summary template.

The instructions here go to the *client* (the owner) — the patient is the
animal and obviously isn't the reader.

## Goal

Translate the clinical plan into instructions an owner can act on without a
veterinary background:

- A short plain-language summary of what was discussed.
- Concrete action items (medications with clear dosing/timing instructions,
  activity restrictions, scheduling a recheck).
- Warning signs that should prompt the owner to seek urgent/emergency care.

## Constraints

- Target roughly a 6th-8th grade reading level. Avoid unexplained veterinary
  jargon.
- Never introduce a medication, dose, or instruction that wasn't part of the
  veterinarian's stated plan.
- Always include at least one clear "when to seek emergency care" item when
  the visit involves a condition with plausible red-flag symptoms.

## Worked examples

Both drawn from real (synthetic) model runs.

### Example 1: canine, suspected GDV

Plan (input to this skill): emergency radiographs, IV fluids, possible
emergency surgery tonight, close monitoring.

Expected client instructions:

- **Summary**: "Your dog is showing signs (distended, tight abdomen,
  retching without bringing anything up, and restlessness) that are very
  concerning for a condition called gastric dilatation-volvulus (GDV),
  sometimes called 'bloat.'... We are taking an X-ray right away to confirm
  this and starting IV fluids to help stabilize him."
- **Action items**: "Be prepared to discuss and consent to emergency surgery
  tonight if GDV is confirmed," "Do not offer food or water to your dog
  until the veterinary team says it is safe to do so."
- **Warning signs**: "Collapse, extreme weakness, or pale/white gums,"
  "Rapid, labored breathing or continued unproductive retching."

### Example 2: feline, suspected urethral obstruction

Plan (input to this skill): IV fluids, sedation and urinary catheterization,
bloodwork, overnight hospitalization.

Expected client instructions (excerpt):

- **Action items**: "Do not offer food or water at home tonight — he will
  be managed in the hospital," "Once discharged, watch closely for
  straining or crying in the litter box again — call us immediately if this
  recurs."
- **Warning signs**: "Straining to urinate again after treatment," "Crying
  or vocalizing in pain," "Lethargy or collapse."

Both examples translate clinical detail into plain language without
inventing anything beyond what the plan stated — no doses or medications
appear in either example because the source transcripts didn't specify any.

## TODO before this skill is production-ready

- [x] Add a few worked examples (input plan -> expected instructions) using
      synthetic vet ER transcripts.
- [ ] Confirm target reading-level tooling/validation with the product
      owner.
- [ ] Decide whether instructions should be localized/translated.
- [ ] Add eval cases checking that no unstated medication/dose leaks in.
