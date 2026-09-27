# apx-example

Template for an [Action Platform](https://github.com/actionplatform/action-platform) plugin — an *apx*, Action Platform extension; every package is named `apx-<slug>`. Every extension point once, small enough to read in one sitting:

| File | Extension point |
|---|---|
| `plugin.py` | the `Plugin`: slug, `needs`, `options` (one with a setup button), `register`, `after_release`, `after_deploy` |
| `tools.py` | MCP tools `example_hello` and `example_remember`, with input and output schemas; `remember` writes the plugin's options store |
| `cli.py` | `action-platform example hello` |
| `rules.py` | a replaced core slot (`gitflow_rules`) — stricter branch kinds while the plugin is enabled |
| `release.py` | named providers: `[release] strategy = "calver"`, `[release] changelog = "plain"` |
| `target.py` | the `DeployTarget` for the `example` cloud — `preflight`, `readiness`, `deploy`, `verify`, `diagnose`, `delete` — composing the parts below through `parts(spec)` |
| `abc.py`, `spec.py` | one ABC per responsibility (`Cloud`, `Readiness`); a frozen `Spec` per call |
| `cloud.py`, `checks.py` | the implementations: the overlay's script (streams its output to the job log), the readiness checks |
| `tests/fake.py`, `tests/live/` | the cloud in memory for fast tests; a suite against the real destination, skipped without it |
| `overlays/` | a cloud overlay `example` — plain files, copied as they are by `action-platform cloud set example`; add a `cookiecutter.json` only when the files need rendering |

## For agents and editors

`SPEC.md` is the contract a plugin follows. `skills/create-plugin/SKILL.md` walks an agent through creating `apx-<slug>` from here — installable in Claude Code (`/plugin marketplace add actionplatform/apx-example`, then `/plugin install apx-example@apx-example`), read by Codex through `.codex-plugin/`, and mirrored for Cursor in `.cursor/rules/plugin.mdc`. `AGENTS.md` holds the repository rules every agent reads.

## Use this template

1. Create a repository from it, named `apx-<slug>`.
2. Rename `apx_example` → `apx_<slug>`, `example` → `<slug>` in `pyproject.toml` (package name, entry points), `plugin.py` (`slug`), `target.py` (`name`), `cli.py`, `overlays/index.json`.
3. Delete what you do not need; a plugin with only `plugin.py` and one tool is fine.
4. `pip install -e ".[dev]"`, `pytest`, `action-platform plugin list` (shows `example` once installed).
5. Publish to PyPI; open a pull request to [plugins-index](https://github.com/actionplatform/plugins-index) with `<slug>.json`.

## Rules

- `register` only declares; no I/O, threads or connections at import or in `register`.
- No monkey-patching of `action_platform.*` — replace a slot (`surface.core.replace`) or ask for a hook.
- `needs` lists every host you talk to and every environment variable you read.

Reference: [writing a plugin](https://github.com/actionplatform/action-platform/blob/master/docs/contribute_plugins.md) · [plugins](https://github.com/actionplatform/action-platform/blob/master/docs/use_plugins.md).
