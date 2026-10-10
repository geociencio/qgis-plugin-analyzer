---
name: release-qgis-plugin-analyzer
description: Project-specific overlays for releasing qgis-plugin-analyzer on top of the framework /release-package workflow.
trigger: when preparing a release, bumping the version, or running /release-package.
---

# Release — qgis-plugin-analyzer Overlay

Project-owned deltas layered on the framework `/release-package` workflow and the
`release-management` skill. The framework covers the generic path; apply these
specifics on top.

## When to use this skill
- When bumping `qgis-plugin-analyzer`'s version.
- When running `/release-package`.
- When writing the CHANGELOG / release notes / development log for a release.

## Non-negotiables

1. **Version in two places** (must match the tag):
   - `pyproject.toml` → `version`
   - `uv.lock` → the `qgis-plugin-analyzer` package `version`
   - The runtime version is **derived dynamically** (`src/analyzer/__init__.py` reads
     `pyproject.toml` / installed metadata), so there is **no** `__version__` string to
     hand-edit. Verify with `uv run qgis-analyzer --version`.
2. **Keep `mypy`.** Unlike some sibling projects, this one enforces typing. Run
   `uv run ruff check . && uv run mypy src/`.
3. **PyPI is manual.** The maintainer runs `uv run twine upload dist/*`. The agent
   stops at `python -m build` + `twine check dist/*` and creates the GitHub release
   with `gh`.
4. **Sync the agentic ground truth.** Run `uv run python scripts/sync_metrics.py`
   so `.agent-state/memory/agent_metrics.json` matches reality (tests + quality).
5. **Separate `chore(docs)` commit.** Self-analysis regenerates the root artifacts
   (`AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`); commit them
   separately from the release bump.
6. **Complete `git add` set.** `src/`, `tests/`, `AGENTS.md`, `forge.toml`,
   `.agent-state/`, `docs/` (the framework workflow list is incomplete).

## Order of operations

1. Confirm green: `uv run ruff check . && uv run mypy src/ && uv run python -m pytest tests/ -q`.
2. Bump the two version sites; verify `uv run qgis-analyzer --version`.
3. Update `CHANGELOG.md` (move `[Unreleased]` → `[X.Y.Z] - YYYY-MM-DD`) and
   create `docs/releases/notes/vX.Y.Z.md`; add a `docs/DEVELOPMENT_LOG.md` entry.
4. `uv run python scripts/sync_metrics.py`; regenerate artifacts.
5. Commit: `chore(release): prepare vX.Y.Z`; commit artifacts as `chore(docs): ...`.
6. `rm -rf dist/ && uv run python -m build && uv run twine check dist/*`.
7. `git tag -a vX.Y.Z -m "Release vX.Y.Z"`; `gh release create vX.Y.Z --notes-file ...`.
8. Hand `uv run twine upload dist/*` to the maintainer.

## Quality Checklist
- [ ] Are both version sites updated and consistent (`--version` matches)?
- [ ] Did `ruff check` + `mypy src/` + `pytest` pass?
- [ ] Is `agent_metrics.json` synced?
- [ ] Is there a `chore(docs)` commit for regenerated artifacts?
- [ ] Is `twine check` clean and the GitHub release created (PyPI left to the maintainer)?
