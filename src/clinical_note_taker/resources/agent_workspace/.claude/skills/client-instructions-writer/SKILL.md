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

## TODO before this skill is production-ready

- [ ] Confirm target reading-level tooling/validation with the product
      owner.
- [ ] Decide whether instructions should be localized/translated.
- [ ] Add eval cases checking that no unstated medication/dose leaks in.
