# Roadmap

This is the durable source of truth for where this project is headed —
read this before opening a new PR or starting a new working session, so
context doesn't need to be re-derived from scratch each time.

For granular, assignable work items, see the [GitHub Milestones](https://github.com/chaa-loftin-jr/clinical-note-taker-agent/milestones)
and the issues under each. This file is the "why" and the big picture; the
issues are the "what, right now."

## Vision

A privacy-conscious AI scribe for veterinary ER encounters — built with
rigorous, demonstrable AI-engineering practice (skills, tools, evals,
CI/security hygiene), real enough that a working vet ER could actually use
it, and structured so the core pattern (transcript → note → coding → client
instructions) can be forked for other clinical domains.

This project intentionally serves three goals at once, in this priority
order when they conflict:

1. **A real tool** — good enough that an actual veterinary ER could use it.
2. **A demonstration of solid AI-engineering practice** — skills, tools,
   evals, and software-engineering hygiene as first-class citizens, not
   afterthoughts.
3. **An open-source starter template** — general enough that someone could
   fork it for a different clinical domain without rewriting the core.

When these pull in different directions, build for (1) first — a working
real-world tool built well *is* the demonstration, and generalizing (3)
before there's one concrete, working implementation to generalize from
tends to produce the wrong abstraction.

## Current state

See the README's [Known Limitations & Roadmap](README.md#known-limitations--roadmap)
section for the up-to-date, code-level list of what's stubbed vs. real.
Short version as of this writing: the full orchestration/tools/skills
pipeline is wired and tested, but `ClinicalNoteAgent.generate()` doesn't
actually parse a response yet, and the SNOMED CT codes are unverified.

## Milestones

| Milestone | Goal | Exit criteria |
|---|---|---|
| [M1: Core Generation Pipeline](https://github.com/chaa-loftin-jr/clinical-note-taker-agent/milestone/1) | Make the agent actually generate a note | `clinical-note-taker generate` produces a real, useful draft end-to-end |
| [M2: Trustworthy Coding & Data](https://github.com/chaa-loftin-jr/clinical-note-taker-agent/milestone/2) | Make the output something a vet can trust | Coding suggestions are review-quick, not redo-from-scratch |
| [M3: Evaluation Rigor](https://github.com/chaa-loftin-jr/clinical-note-taker-agent/milestone/3) | Know when a change makes things better or worse | Deterministic + LLM-judge evals with tracked scores over time |
| [M4: Real-World Usability](https://github.com/chaa-loftin-jr/clinical-note-taker-agent/milestone/4) | Make it something a real ER would actually use | Input modality, interface, review workflow, and deployment all decided and built |
| [M5: Generalization](https://github.com/chaa-loftin-jr/clinical-note-taker-agent/milestone/5) | Prove the core pattern generalizes | A second domain profile exists and works without rewriting the core |
| [M6: Polish & Distribution](https://github.com/chaa-loftin-jr/clinical-note-taker-agent/milestone/6) | Make it releasable and presentable | Release process, docs, and a demo exist |

Milestones are ordered by priority, not necessarily strict sequencing —
some M2/M3 work can happen in parallel with M1 once the output contract
exists. M4 (usability) deliberately comes after the pipeline is trustworthy
(M2/M3): a usable interface on top of an unreliable pipeline isn't worth
building yet.

## Working agreement for future sessions/contributors

- Keep `SKILL.md` files, `models.py`, and `evals/cases/*.yaml` in sync: the
  schema is the contract, skills target it, eval cases verify it.
- Never commit real client/patient transcripts — synthetic only, as in
  `evals/cases/`.
- Update this file's "Current state" pointer (or just trust the README's
  Known Limitations section, which should stay current) when a milestone's
  exit criteria are met, and close out the milestone on GitHub.
