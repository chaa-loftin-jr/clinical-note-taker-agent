# clinical-note-taker

Project scaffold — the agent implementation lives in a separate PR
([#1](https://github.com/chaa-loftin-jr/clinical-note-taker-agent/pull/1)).
This branch establishes the generic project tooling, CI, and Docker setup.

## Setup

```bash
uv sync
```

## Dev commands

```bash
uv run ruff check .          # lint
uv run ruff format --check . # format check
uv run mypy src               # typecheck
uv run pytest                 # test
uv run bandit -r src -c pyproject.toml  # static security scan
uv build                      # packaging sanity check
```

## Docker

```bash
docker build -t clinical-note-taker .
docker run --rm clinical-note-taker
```

## CI

GitHub Actions runs lint, typecheck, tests (matrix across supported Python
versions), a packaging build check, bandit + pip-audit security scans,
gitleaks secret scanning, dependency review on pull requests, and a weekly
CodeQL scan. Dependabot keeps Python and Action dependencies up to date.
