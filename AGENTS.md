# AGENTS.md

Rules an AI agent (or a new contributor) follows in this repository — and in any `apx-<slug>` started from it.

## What this is

A template for an Action Platform plugin. The contract is `SPEC.md`; the skill in `skills/create-plugin/` walks through creating a plugin from here. Read `SPEC.md` before changing anything.

## Code

- Python 3.11+, `ruff check . && ruff format --check .`, `pytest` green before a commit.
- No comments inside function bodies; no test docstrings. Module docstrings say what the module is for.
- `register` declares only — no I/O, threads or connections at import or in `register`.
- Never monkey-patch `action_platform.*`; replace a slot or ask for a hook.
- Long commands go through `action_platform.core.process.stream` so their output reaches the platform's job log.
- `needs` lists every host and environment variable the plugin touches.
- One ABC per responsibility (`abc.py`), a `Spec` per call, the target composing them through `parts()`; `tests/fake.py` built from the real service's answers, `tests/live/` against the real destination.

## Commits and branches

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): `type(scope): description`; one commit per concern; stage files explicitly. Git-flow: `<kind>/<issue>-<slug>` from `master`, kinds `feature bugfix hotfix release chore docs refactor test ci perf`; never commit on `master`. One pull request per issue.

## Release

`action-platform release <level>`; the tag publishes to PyPI; then a PR to `plugins-index` with the new `latest`.
