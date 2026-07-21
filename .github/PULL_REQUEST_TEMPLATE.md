## Identifier

<!-- Issue #, Jira ticket #, or other tracking reference. Delete whichever doesn't apply. -->
Closes #
<!-- Jira: PROJ-123 -->

## Semantic commit

<!-- One line, conventional-commit style, summarizing this PR as it should read in history -->
<!-- e.g. feat(agent): add retry logic for malformed submissions -->

## Description

<!-- What does this change do, and why? Link context a reviewer wouldn't otherwise have. -->

## Testing

<!-- How do you know this works? Prefer real evidence over a checklist — command output, a
     real end-to-end run, the actual eval harness result — over "tested locally". -->

- [ ] `uv run pytest` passes
- [ ] `uv run ruff check . && uv run mypy src` clean
- [ ] Verified against real behavior (not just unit tests) where the change touches generation
      logic, prompts, or skills — paste the actual output
