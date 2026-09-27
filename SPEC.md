# Writing an Action Platform plugin — the spec

A plugin is a Python package named `apx-<slug>` that the platform discovers through entry points. This file is the contract; the code in this repository is the smallest complete example of it.

## 1. Package

| Item | Rule |
|---|---|
| Name | `apx-<slug>` on PyPI, module `apx_<slug>`; the slug is `[a-z0-9-]`, not one of `core platform official admin system test internal` |
| Dependency | `action-platform>=<min_core>`; `min_core` on the `Plugin` says the same |
| Entry points | `action_platform.plugins` → the `Plugin` class; `action_platform.deploy_target` → each `DeployTarget` (name = the cloud, `aws/lambda`); optional `action_platform.ci_runner`, `action_platform.source_host`, `action_platform.release_strategy`, `action_platform.changelog` |
| Layout | `apx_<slug>/{plugin.py, target.py, tools.py, cli.py, overlays/}`, `tests/`, `pyproject.toml`, `LAST_VERSION`, `CHANGELOG.md`, `platform.toml`, `AGENTS.md` |
| Style | no comments inside function bodies, no test docstrings, `ruff check && ruff format --check` clean, `pytest` green |

## 2. `Plugin` (`action_platform.abc.Plugin`)

```python
class MyPlugin(Plugin):
    slug = "my-cloud"
    name = "My Cloud"
    description = "One line"
    min_core = "0.32"
    needs = ["tool: mycloud-cli", "env: MYCLOUD_REGION", "net: api.mycloud.com"]
    options = [Option(key="project_id", label="Project", kind="text", required=True)]

    @property
    def overlays(self) -> Path:
        return Path(__file__).parent / "overlays"

    def register(self, surface: Surface) -> None:
        surface.cli.add_typer(cli.app, name="my-cloud")
```

`overlays` points at a folder shaped like the templates repository; `register` declares only (tools, commands, slots); `after_release(ctx)` and `after_deploy(results)` are optional hooks.

- `needs` lists every host the plugin talks to and every environment variable it reads; the CLI shows it before installing.
- `options` are what an organization fills in under Plugins → Configure; the platform stores them and passes each to a deploy as `AP_<SLUG>_<KEY>` (upper case, `-` → `_`) in `ctx.env`, plus `AP_APP=<org>/<project>/<app>`.
- `register` declares only. No network, no threads, no file writes at import or in `register`.
- Never monkey-patch `action_platform.*`; replace a slot (`surface.core.replace("gitflow_rules", MyRules)`) or ask for a hook.
- Log through `self.logger` (or `action_platform.logging.logger`): it reaches the platform's job log.

## 3. `DeployTarget` (`action_platform.abc.DeployTarget`)

| Method | Must | Notes |
|---|---|---|
| `preflight(ctx)` | raise `DeployError` when tooling, files or credentials are missing | runs before every deploy and on dry runs |
| `deploy(ctx)` | ship `ctx.next_version` to `ctx.stage`; return `DeployResult(ok, target, version, url)` | run long commands with `action_platform.core.process.stream(...)` so every line reaches the job log; `ctx.stage` is the **scope's name** (`dev`, `prod-eu`…), use it in resource names |
| `readiness(ctx) -> list[Check]` | say what can be verified **without building or changing anything**: credentials, permissions, destination state, a version already published | each `Check(id, ok, detail, level="target", severity="error"|"warning", fix)`; `error` blocks the deploy, `warning` informs; ids `<area>.<what>` (`aws.permissions`, `stack.state`) |
| `verify(version, stage)` | whether `version` is really at the destination | called after any executor reported success |
| `url(version, stage)` | where it can be seen | optional |
| `diagnose(ctx)` | `Diagnosis(ok, target, status, url, details)` | |
| `delete(ctx)` | tear the stage down | idempotent |
| `rollback(ctx, to_version)` | optional | raise `NotImplementedError` when the cloud cannot |

Credentials: never a long-lived key in the plugin. Prefer a token the platform signs (`ctx.identity_token(audience)`) exchanged at the cloud (OIDC / a proxy in the user's account), else the cloud CLI's own chain.

## 4. Overlay (`overlays/cloud/<cloud>/`)

Shaped like the templates repository: `cookiecutter.json`, `{{cookiecutter.project_slug}}/`, `hooks/post_gen_project.py`, and `overlays/index.json` declaring the cloud (`id`, `types`, `languages`, `description`). The platform merges it into the matrix when the plugin is installed.

**One overlay for every language.** The contract every web project honours is *serve HTTP on `$PORT`*, and the build is `ap-build package` (from [images-base](https://github.com/actionplatform/images-base)): it assembles the app, its dependencies and `run.sh` (`exec <start command>`) — or `bootstrap` for Go — for any language. So the overlay is:

- one IaC file (`template.yaml`, a Dockerfile, a workflow…) with the runtime chosen by `{{ cookiecutter.language }}`;
- a one-line `Makefile`: `build-Function: AP_ARTIFACTS="$(ARTIFACTS_DIR)" ap-build package`;
- `requirements/` — the least-privilege policy the deploy needs;
- `DEPLOY.md` — how to set it up by hand.

No `_lang/<language>/` folders, no handler files. [apx-aws-lambda](https://github.com/actionplatform/apx-aws-lambda) is the reference.

## 5. Tools and commands

MCP tools come out as `<slug>_<name>`; annotate them (`READ_ONLY`, `REACHES_OUT`, `DESTRUCTIVE`) and give input and output schemas. CLI commands live under `action-platform <slug> …`. Both must refuse to run while the plugin is disabled (the surface does that for tools).

## 6. Tests

`pytest` with no network: mock the cloud CLI (`shell.run` / `stream`), assert the commands built, the `Check`s returned and the `DeployResult`. Cover `readiness` for the failure the user will actually hit (missing credentials, wrong permission, resource in a bad state).

## 7. Release and publish

1. Git-flow: `<kind>/<issue>-<slug>` branches, Conventional Commits, one PR per issue.
2. `action-platform release <patch|minor|major>` bumps `LAST_VERSION`, `pyproject.toml`, `CHANGELOG.md`, tags `vX.Y.Z`; CI publishes to PyPI on the tag.
3. Open a PR to [plugins-index](https://github.com/actionplatform/plugins-index) with `plugins/<slug>.json` (`pypi`, `latest`, `min_core`, `needs`, `tags`); leave `verified: false`.
4. If the platform's worker must carry a tool the plugin shells out to, open an issue on action-platform.

## 8. Checklist before the first PR

- [ ] `pip install -e ".[dev]" && ruff check . && ruff format --check . && pytest`
- [ ] `action-platform plugin list` shows the slug; `action-platform cloud set <cloud>` renders the overlay for every language it declares
- [ ] `readiness` returns at least one `Check`; `deploy` streams its output
- [ ] `needs` complete; no I/O at import; no monkey-patching
- [ ] README: what it deploys, what it needs, how credentials flow
