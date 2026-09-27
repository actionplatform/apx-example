---
name: create-plugin
description: Create a new Action Platform plugin (apx-<slug>) from the apx-example template — a deploy target with readiness, a one-file overlay for every language, tools, tests, release and the plugins-index entry.
---

# Creating a plugin

The contract is `SPEC.md` in this repository; read it first. A plugin is a PyPI package `apx-<slug>` found through entry points.

1. **Name it.** Ask for the slug (`gcp-cloudrun`, `dokploy`) and the cloud id the overlay declares (`gcp/cloudrun`). Refuse reserved slugs (`core platform official admin system test internal`).
2. **Copy the template.** New repository `apx-<slug>` from this one. Rename `apx_example` → `apx_<slug>` everywhere: `pyproject.toml` (name, entry points), `plugin.py` (`slug`, `name`, `description`, `min_core`), `target.py` (`name` = the cloud id), `cli.py`, `overlays/index.json`, tests. Delete `release.py` and `rules.py` unless the plugin replaces a strategy or a slot.
3. **`needs` and `options`.** Ask what the target talks to (hosts), what it reads (env vars), what an organization must configure (region, project id, token…). Write `needs` and `options` on the `Plugin`; each option arrives at a deploy as `AP_<SLUG>_<KEY>` in `ctx.env`.
4. **The target.** Follow SPEC.md's *Structure*: an ABC per responsibility in `abc.py`, a `Spec` per call in `spec.py`, one module per implementation, `checks.py` for readiness, and `target.py` composing them through `parts(spec)`. In `target.py`, implement `preflight`, `deploy`, `readiness`, `verify`, `url`, `diagnose`, `delete` with the cloud's CLI through `stream(...)`. `ctx.stage` is the scope's name — put it in resource names. `readiness` returns `Check`s for credentials, permissions and destination state; nothing built, nothing changed. Credentials: the platform's identity token (`ctx.identity_token(audience)`) exchanged at the cloud, or the CLI's own chain — never a stored key.
5. **The overlay.** `overlays/cloud/<provider>/<service>/`: one IaC file with the runtime picked by `{{ cookiecutter.language }}`, a `Makefile` whose only recipe runs `AP_ARTIFACTS="$(ARTIFACTS_DIR)" ap-build package`, `requirements/` with the least-privilege policy, `DEPLOY.md`. No `_lang/` folders: every web project serves HTTP on `$PORT` and `ap-build` packages it. Declare the cloud in `overlays/index.json` (`id`, `types`, `languages`, `description`).
6. **Tests.** `tests/fake.py` stands in for the service — built from what the real API answers (read its source or reference), never from what the plugin expects; swap it in through `parts()`. Assert calls, `Check`s and `DeployResult`. Add `tests/live/` against the real destination, skipped without credentials, and run it in CI when the destination can be stood up there. Render the overlay for each language with `cookiecutter --no-input … language=<l>` and validate the IaC file with its linter.
7. **Verify locally.** `pip install -e ".[dev]"`, `ruff check .`, `pytest`, `action-platform plugin list`, `action-platform cloud set <cloud>` on a generated project, `action-platform readiness --scope dev`, `action-platform deploy --dry-run`.
8. **Ship.** Git-flow branch per issue, Conventional Commits, PR. `action-platform release minor` tags and publishes. Then a PR to `actionplatform/plugins-index` adding `plugins/<slug>.json` with `verified: false`. If the platform's worker needs a CLI the target shells out to, open an issue on `actionplatform/action-platform`.

Rules that always apply: no I/O at import or in `register`; no monkey-patching; no comments inside function bodies; one PR per issue.
