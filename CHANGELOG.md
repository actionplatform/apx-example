# Changelog

## v0.3.0 — 2026-09-27

### Features
- the template shows one ABC per responsibility, a fake and a live suite

### Bug Fixes
- **tests:** import the matrix from scaffold.catalog

### Docs
- **spec:** the Plugin snippet as ruff formats it
- SPEC.md, AGENTS.md, the create-plugin skill and manifests for Claude Code, Codex and Cursor

### Tests
- make tests a package so test_target imports the fake

## v0.2.0 — 2026-09-19

### Features
- **target:** the template shows a DeployTarget with readiness
- tools read and write the plugin's options store

## v0.1.0 — 2026-09-15

### Features
- template plugin — tool, command, overlay, release strategy, replaced slot, hooks

### Refactoring
- package apx-example, tools as example_<name>
- overlay as plain files, no cookiecutter

### CI
- explicit ruff rule set
- publish to PyPI on release with trusted publishing; code quality on pull requests
