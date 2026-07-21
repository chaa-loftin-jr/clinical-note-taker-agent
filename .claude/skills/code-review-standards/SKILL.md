---
name: code-review-standards
description: Review a diff or PR the way a senior engineer at a top-tier company would — clean code, readability, extensibility, and zero tolerance for anti-patterns, with every claim checked against the actual code before it's written down. Use when asked to review a PR, review a diff, do a code review, or check code quality/standards on this repo.
---

# Code Review Standards

This is how code review works on this repo. It applies to Python source,
tests, eval cases, and CI/workflow files — not prose docs (README/SKILL.md
changes get a lighter pass: accuracy and staleness matter, style doesn't).

## Voice

Write like a senior engineer, not a linter. Direct, specific, and evidence-based —
never hedge with "might want to consider" when something is actually wrong, and
never invent severity to sound thorough. A clean PR gets told it's clean.

- Cite line numbers and quote the actual code. "This could be cleaner" is not
  a finding; "line 42 does X, which breaks when Y, here's the fix" is.
- Every finding must be something you verified by reading the code — not a
  pattern that's "usually" a problem. If you're not sure a claim is true,
  check before writing it down (grep the codebase, read the dependency's
  source, run the test). See "Verify before you write it down" below.
- Say why something matters, not just that it violates a rule. "Unbounded
  retry loop" is a description. "Unbounded retry loop means a single flaky
  model response burns your entire per-request budget" is a finding.
- Call out good engineering as specifically as you call out bad engineering.
  If a test double was redesigned well, or an exception chain was preserved
  correctly, say so — and say *why* it's good, not just "nice test." A review
  that's 100% criticism reads as reflexive, not calibrated.

## Severity levels

Use these consistently and say which one applies to each finding:

- **🔴 Blocking** — will cause a bug, a regression, a security issue, or ships
  something the PR's own description says isn't true yet. Don't approve past
  this without it being fixed or explicitly deferred with a reason.
- **🟡 Worth a comment** — real issue, not urgent. Debt that should be tracked,
  a design choice you'd have made differently but can defend either way, a gap
  the author already flagged as known/deferred (still worth naming, so it
  doesn't silently become permanent).
- **🟢 Positive** — specific things done well. Not a participation trophy —
  only include what you'd actually point to as an example for someone else.
- **Nit** — real but trivial (naming, a slightly clearer structure). Never
  blocking. Say so explicitly so the author knows they can ignore it.

## What to actually look for

**Correctness & control flow**
- Exception handling: is the *right* exception caught? Is the cause chain
  preserved (`raise X from e`), or does a retry/fallback path silently lose
  the original error? A "last error" or "last seen" variable that's only
  updated in some branches is a classic, easy-to-miss bug — trace every
  branch that can reach the place it's read.
- Resource cleanup: does a context manager (`async with`, `with`) actually
  wrap everything that needs it, and does cleanup happen before an exception
  propagates, not after? This matters more in async code, where it's easy to
  raise from outside a scope you meant to still be inside.
- Retry/loop bounds: is there always a way out? Does the loop variable
  (attempt count, remaining budget) actually get consumed on every iteration,
  including error paths?

**Clean code & readability**
- Names should say what something is, not require reading the body to find
  out. `_collect_submission` vs `_find_submission` — fine, because the names
  actually differ in a way that matches their behavior (drain a turn vs.
  scan one message). If two functions need a comment to explain why they're
  not the same function, consider whether they should be.
- Comments explain *why*, not *what*. A comment restating the next line in
  English is noise. A comment explaining a non-obvious constraint, a past
  incident, or a deliberate tradeoff is load-bearing — keep it, and check
  it's still true.
- Duplication in tests is still duplication. A test helper that turns a
  15-line literal into 3 readable lines is a real improvement, not
  gold-plating — flag it as positive when you see it done well.

**Extensibility & anti-patterns**
- Premature abstraction is an anti-pattern too. Don't ask for a config
  system, a plugin architecture, or a base class for something that has one
  implementation and no stated plan for a second. YAGNI cuts both ways: reward
  code that resisted over-engineering as much as you'd flag code that
  under-engineered something that's about to grow.
- Watch for logic that only works by accident of the current call pattern —
  e.g., a loop that "happens" to always terminate because of how it's
  currently called, not because the code enforces it. That's a latent bug,
  not a working feature.
- Check whether a change duplicates something that already exists elsewhere
  in the codebase (a validation rule, an error type, a retry pattern) instead
  of reusing or extending it.

**Tests**
- A test that can't fail is worse than no test — check that assertions
  actually exercise the changed behavior, not just that the function ran
  without raising.
- Mocks/fakes should model the real dependency's actual contract, not a
  convenient simplification of it. If the fake and the real thing can diverge
  silently, say so.
- No network/API calls in the unit suite for this repo — anything that needs
  a live model call belongs in `evals/`, not `tests/`. Flag it if you see the
  line blurred.

**Security & data handling**
- No secrets, API keys, or real client/patient data in code, comments, fixtures,
  or eval cases — this repo's eval cases must stay synthetic.
- PII/PHI-adjacent handling changes (redaction, logging) get extra scrutiny —
  see `SECURITY.md`.

## Verify before you write it down

This repo's own history is full of review findings that turned out to hinge
on a claim someone could have gotten wrong — "does the SDK validate this
before it reaches our code?", "is this config value actually read anywhere?",
"does this test really exercise the retry path?". Before a finding goes in
the review:

- If the claim is about *this codebase*: grep for it. Don't assert a value
  "is never read elsewhere" without checking.
- If the claim is about a *dependency's behavior*: check its source or docs,
  don't rely on general knowledge of how similar libraries "usually" work.
- If the claim is about *test coverage*: read the test, don't infer from its
  name.

A finding that turns out to be wrong after you've stated it with confidence
costs more credibility than three correct findings earn back. When you
genuinely can't verify something (e.g., real-world model non-determinism),
say that explicitly instead of asserting either way.

## Output shape

End with an explicit verdict: **Approve**, **Approve with nits**, or
**Request changes**, plus one sentence on why. The reader should be able to
stop after the verdict line and know what to do next; everything above it is
support for that conclusion, not a substitute for stating it.
