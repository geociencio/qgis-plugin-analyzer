# Agentic Forge v1.4.1 — Release Verification & Delta

**Release**: `v1.4.1` — annotated tag `8d7a510` → commit
`537f9fdfdad03114d482abc8b5244939c52363c0`, dated 2026-10-18, titled
*"qa-docker compatibility alias"*.

**Base release**: `v1.4.0` — commit `5f9c665`, *"tests, CI and configurable tooling"*.

**Upstream**: `https://codeberg.org/geociencio/agentic-forge.git`; tags `v1.4.0` and
`v1.4.1` verified with `git fetch origin --tags` / `git ls-remote`.

**Analyzed**: 2026-10-19, by extracting the tag with `git archive` and running the
framework's own CI-equivalent checks, isolated probes and a dry-run upgrade against this
repository's real `.agent-state/` and `forge.toml`.

**Applied**: this repository was upgraded to `v1.4.1` and committed as
`a98f5a8 chore(agent): bump agentic-forge to v1.4.1`.

> **Update (2026-10-19)**: `v1.4.2` (`b264e35`) supersedes this release and fixes the
> remaining mypy/TOML error and cache-aware metric scanning. This document is kept as the
> **v1.4.1 intermediate delta**; for the current status and applied upgrade, see
> [AGENTIC_FORGE_v1.4.2_UPDATE.md](AGENTIC_FORGE_v1.4.2_UPDATE.md).

**Base documents**: [AGENTIC_FORGE_v1.3.0_UPDATE.md](AGENTIC_FORGE_v1.3.0_UPDATE.md) and
[DEEP_ANALYSIS_AGENTIC_FORGE_v1.2.0.md](DEEP_ANALYSIS_AGENTIC_FORGE_v1.2.0.md). Findings
`F-01`…`F-15` refer to the original audit.

---

## 1. What v1.4.0 / v1.4.1 contain

### v1.4.0 — tests, CI and configurable tooling

- **Test suite** under `tests/` (validator, graph, memory pruning, lesson extraction,
  project commands): 33 tests.
- **CI**: `.github/workflows/ci.yml`, `.forgejo/workflows/ci.yml`, `scripts/ci.sh`;
  matrix Python **3.9 / 3.11 / 3.13**; runs Ruff, format, mypy, pytest and the framework
  validators.
- **`forge.py --version`** backed by a `VERSION` file (`1.4.1`).
- **`forge.py project <test|test-full|lint|format|type|bump>`**, driven by
  `[project]` keys in `forge.toml`.
- **Consumed config**: `test_command`, `test_command_full`, `lint_command`,
  `format_command`, `type_command`, `max_lesson_lines`, `strict_agent_system`.
- **Python 3.9 support**: `tomli` fallback, `requirements.txt` / `requirements-dev.txt`.
- **Scaffold validation**: domain-pack skills/workflows validated; templates marked
  `template: true`; the `audit-plugin` reference was fixed to use `qgis-core`.
- **Genericization**: metrics are data-driven (no hardcoded analyzer name), the lesson
  extractor uses the full diff and no longer names a specific analyzer, documentation
  paths are generic, `QUICK_REFERENCE` is synchronized with frontmatter (regression test).
- **Skill merge**: `qa-docker` merged into `testing-standards`; Docker/mock guidance is
  no longer duplicated.

### v1.4.1 — compatibility alias

- Restores `skills/qa-docker/SKILL.md` as a **deprecated alias** pointing to
  `testing-standards`, so v1.3.x overlays/`AGENTS.md` links keep validating for one
  release. The alias contains no duplicated guidance.
- Updates `VERSION` to `1.4.1`, README/QUICK_REFERENCE/AGENTS and a regression test.

---

## 2. Verification

### 2.1 Framework self-quality (standalone checkout)

| Check | Result |
| :--- | :--- |
| `ruff check .` (`ruff.toml`, py39) | ✅ All checks passed |
| `ruff format --check .` | ✅ 19 files already formatted |
| `mypy tools tests` | ❌ 2 errors: `tomli` import (environment-only; installed by CI) and `tools/forge_paths.py:54` *"Exception type must be derived from BaseException"* |
| `pytest tests -q` | ❌ **30 passed, 2 failed, 1 skipped** in a standalone checkout |
| `scripts/ci.sh` (local reproduction) | ❌ red: the two pytest failures + the `forge_paths.py:54` mypy error |
| `forge.py --version` | ✅ `agentic-forge 1.4.1` |

**Why the two tests fail standalone** — they are consumer-coupled:

1. `tests/test_validator.py::test_all_skill_files_pass_validation` asserts that
   `project-context` is among the skills. That is a **project overlay** skill, not a
   framework skill; it exists in this repository and in SecInterp, not in the framework.
2. `tests/test_validator.py::test_project_paths_are_resolved` asserts that
   `.agent-state/memory/agent_metrics.json` and `memory_policy.md` exist. The framework
   repository has no `.agent-state/`.
3. `tests/test_cli.py::test_project_config_keys_are_loaded` additionally requires
   `strict_agent_system = true` in the consumer's `forge.toml`.

The suite passes **33/33** when run inside a consumer project with the expected overlay,
state and strict flag (verified here and in §2.2). The framework's own CI, however, runs
`pytest tests` in the standalone checkout and is therefore red. This is a test-design
bug, not a functional regression for consumers.

### 2.2 Upgrade dry-run and applied state in this repository

`.agent` = `v1.4.1`, real `.agent-state/` (6 overlay skills, lessons, metrics), real
`forge.toml` with the new command contract and `strict_agent_system = true`:

| Gate | Result |
| :--- | :--- |
| `forge.py validate` | ✅ 18 skills, 14 workflows, 3 templates; 0 errors |
| `forge.py validate --graph` | ✅ all references valid |
| `forge.py validate --conflicts` | ✅ no conflicts |
| `forge.py metrics validate` | ✅ 38 files, metric-consistent |
| `forge.py memory check` | ✅ 169 lines (limit 350) |
| `forge.py --version` | ✅ 1.4.1 |
| `pytest .agent/tests -q` | ✅ 33 passed |
| `forge.py project test` | ✅ 233 passed (`uv run pytest -q`) |
| `forge.py project lint` | ✅ All checks passed (`uv run ruff check .`) |
| `forge.py project type` | ✅ 72 files (`uv run mypy src/`) |
| Project `ruff` / `mypy` / `pytest` | ✅ / ✅ / 233 passed |

---

## 3. Consumer status after v1.4.1

| Repository | `.agent` state | Gap |
| :--- | :--- | :--- |
| `qgis-plugin-analyzer` | **`v1.4.1`** (`537f9fd`) | ✅ upgraded + committed (`a98f5a8`) |
| `ai-context-core` | `v1.4.1` (`537f9fd`) | ✅ clean; submodule pointer recorded |
| `qgis-plugin-manager` | `v1.4.1` + 3 local edits (`.gitignore`, `tools/forge_metrics_checks.py`, `tools/forge_paths.py`) | pointer drift + small local patch still uncommitted |
| `sec_interp` | `v1.4.1` (`537f9fd`) | submodule content clean; parent pointer still needs a commit |
| local `agentic-forge` checkout | `v1.2.0` | `git fetch origin --tags` (the consumers fetched the tags themselves) |

The ecosystem has largely converged on `v1.4.1`; the remaining work is administrative
(commit the pointers in `sec_interp` and `qgis-plugin-manager`, and upstream the latter's
3-file patch).

---

## 4. Finding-by-finding delta

| ID | v1.2.0 finding | v1.4.1 status | Evidence |
| :--- | :--- | :--- | :--- |
| F-01 | `memory prune` destructive by default | ✅ **Fixed** (v1.3.0) | dry-run default; `--apply` required; verified |
| F-02 | `validate --graph` always exit 0 | ✅ **Fixed** (v1.3.0) | exit 1 on broken refs; verified |
| F-03 | overlay/scaffold not validated | ✅ **Fixed** (v1.4.0) | overlay + templates validated; `audit-plugin` uses `qgis-core`; broken template is a warning |
| F-04 | no tests/CI, lint/type debt | 🟡 **Partial** | tests + CI added, Ruff/format clean; **standalone CI red** (2 consumer-coupled tests + `forge_paths.py:54` mypy) |
| F-05 | fragmented versions, no release | ✅ **Fixed** | `v1.4.0`/`v1.4.1` tags, `VERSION`, `--version`; all four consumers on v1.4.1 |
| F-06 | Python 3.11+ vs consumer 3.9 | ✅ **Fixed** | `tomli` fallback + requirements + CI matrix 3.9/3.11/3.13 |
| F-07 | genericization leaks | ✅ **Fixed** | no `763`/`docs/source`/`qgis_analyzer`/`SecInterp` in core skills/workflows/tools |
| F-08 | `forge.toml` keys ignored | ✅ **Fixed** | `forge.py project` + `strict_agent_system`/`max_lesson_lines` consumed |
| F-09 | metrics false positives / `--fix` risk | ✅ **Fixed** | scaffold excluded, data-driven KPIs, `STALE_MAPPINGS = {}`; 38 files pass |
| F-10 | docs contradictions | ✅ **Mostly fixed** | `QUICK_REFERENCE` 0/14 mismatches; GEN8 now "Partially implemented"; only the loose "pre-commit" wording remains |
| F-11 | `qa-docker`/`testing-standards` overlap | ✅ **Fixed** | merged; `qa-docker` is a deprecated alias with no duplicate guidance |
| F-12 | validator/parser weaknesses | ✅ **Mostly fixed** | `frontmatter.py`, `workflow_graph.py`, `agent_links.py`, full-diff lesson extraction, `--version` |
| F-13 | no changelog / release process | ✅ **Fixed** | CHANGELOG, VERSION, tags, CI workflow |
| F-14 | scaffold is a SecInterp snapshot | ✅ **Fixed** | project `max_cc` thresholds, no project name/test counts, template markers |
| F-15 | structural completeness | 🟡 **Improved, remains** | skill checklists 5/9 (v1.3.0: 5/9); Expected Result 7/14 (was 6/14) |

**Net effect**: the release closes essentially all the v1.2.0 correctness, portability,
genericization and documentation findings. The remaining blockers are the **framework's
own CI being red in a standalone checkout** (F-04) and the **structural-completeness
backlog** (F-15).

---

## 5. Applied changes in this repository (`a98f5a8`)

- `.agent` bumped `v1.3.0` (`5bff43a`) → `v1.4.1` (`537f9fd`).
- `forge.toml` now declares the v1.4 command contract:
  `test_command`, `test_command_full`, `lint_command`, `format_command`,
  `type_command`, plus `strict_agent_system = true`.
- `AGENTS.md`: added the missing `/i18n-maintenance` workflow row; removed the active
  `qa-docker` row and documented it as a deprecated alias; documented the new
  `[project]` command keys.
- `.agent-state/next_steps.md`: recorded the v1.4.1 upgrade and the resolved
  `metrics validate` issue.

Post-upgrade gates: `validate` (18 skills / 14 workflows / 3 templates), `--graph`,
`--conflicts`, `metrics validate` (38 files), `memory check` (169/350), framework tests
(33), project `test`/`lint`/`type`, `ruff`, `mypy` and `pytest` — all green.

> `forge.py project bump` is intentionally **not** configured (`version_bump_command`
> is absent). The project's release process remains `docs/releases/RELEASE_PROCESS.md`
> (manual `pyproject.toml` + `uv lock`); the shared `/release-package` workflow will stop
> at the bump step until a command is provided.

---

## 6. Remaining framework work (recommended for v1.4.2 / v1.5.0)

1. **Make the test suite self-contained**: create framework fixtures for
   `.agent-state/` and the overlay skill, or skip consumer-only tests when
   `[forge].framework` is a standalone checkout; add a CI job that runs the suite both
   standalone and against a fixture project. This is the only reason the new CI is red.
2. **Fix `tools/forge_paths.py:54`**: replace
   `except (OSError, getattr(tomllib, "TOMLDecodeError", ValueError))` with an explicit
   exception type (or a module-level alias) so mypy passes; add `tomli` to the mypy
   environment or `ignore_missing_imports` for it.
3. **Complete the structural checklist**: add Quality Checklists to the four remaining
   skills and Expected Result sections to the seven remaining workflows (or relax
   `verify-standards` to the actual convention and enforce it).
4. **Resolve the `pre-commit` wording**: the framework ships CI, not a pre-commit hook;
   either ship one or say "project-owned pre-commit hooks".
5. **Upstream the `qgis-plugin-manager` 3-file patch** and commit the `sec_interp`
   submodule pointer.
6. **Add `version_bump_command` guidance** to the docs so `/release-package` is usable
   without project-specific scripting (or document the manual fallback).

---

## 7. Reproduction appendix

```bash
# Tags and ancestry
git -C .agent fetch origin --tags
git -C .agent describe --tags
git -C .agent log --oneline v1.3.0..v1.4.1

# Framework self-quality (standalone)
git -C .agent archive v1.4.1 | tar -x -C /tmp/forge141
(cd /tmp/forge141 && ruff check . && ruff format --check .)
(cd /tmp/forge141 && mypy tools tests)        # 2 errors (1 env-only, 1 real)
(cd /tmp/forge141 && pytest tests -q)         # 30 passed, 2 failed, 1 skipped

# Framework gates in this repository
python .agent/tools/forge.py validate
python .agent/tools/forge.py validate --graph
python .agent/tools/forge.py validate --conflicts
python .agent/tools/forge.py metrics validate
python .agent/tools/forge.py memory check
python .agent/tools/forge.py --version
pytest .agent/tests -q                        # 33 passed in project context
python .agent/tools/forge.py project test
python .agent/tools/forge.py project lint
python .agent/tools/forge.py project type
```

---

*Report generated on 2026-10-19 against `agentic-forge` v1.4.1 (`537f9fd`). The `.agent/`
submodule was upgraded and committed in `a98f5a8`; the reports themselves remain
untracked under project-owned `docs/reports/`.*
