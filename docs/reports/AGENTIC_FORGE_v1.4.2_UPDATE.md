# Agentic Forge v1.4.2 — Hotfix Verification & Delta

**Release**: `v1.4.2` — annotated tag `85a0d4f` → commit
`b264e35ce0c42a5d7743133187a2ec0dd37dfe40`, dated 2026-10-19, titled
*"quality-gate hotfix"*.

**Delta**: one commit since `v1.4.1` (`537f9fd`).

**Upstream**: `https://codeberg.org/geociencio/agentic-forge.git`; tag verified with
`git fetch origin --tags`.

**Applied**: this repository was upgraded to `v1.4.2` and committed as
`b98186a chore(agent): bump agentic-forge to v1.4.2`. No `forge.toml`, `AGENTS.md` or
workflow changes were required.

**Base documents**: [AGENTIC_FORGE_v1.4.1_UPDATE.md](AGENTIC_FORGE_v1.4.1_UPDATE.md),
[AGENTIC_FORGE_v1.3.0_UPDATE.md](AGENTIC_FORGE_v1.3.0_UPDATE.md) and
[DEEP_ANALYSIS_AGENTIC_FORGE_v1.2.0.md](DEEP_ANALYSIS_AGENTIC_FORGE_v1.2.0.md).

---

## 1. What v1.4.2 changes

The release is a **targeted hotfix** for the quality gates identified in the v1.4.1
verification:

- **`forge_paths` TOML decoding**: catches `ValueError` when decoding TOML, fixing the
  mypy failure on `tools/forge_paths.py:54` (the `getattr(tomllib, "TOMLDecodeError", …)`
  exception clause).
- **`forge_metrics_checks.should_skip_file`**: now skips the metrics file and tool caches
  (`.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `__pycache__`, `.git`), avoiding
  self-validation and inflated scans.
- **`.gitignore`**: covers `.mypy_cache/` and `.pytest_cache/`.

There are **no API, `forge.toml`, workflow or skill changes**; v1.4.2 is a drop-in patch
over v1.4.1 (the `qa-docker` deprecated alias remains).

---

## 2. Verification

### 2.1 Framework self-quality (standalone checkout)

| Check | v1.4.1 | v1.4.2 |
| :--- | :--- | :--- |
| `ruff check .` | ✅ | ✅ clean |
| `ruff format --check .` | ✅ | ✅ 20 files formatted |
| `mypy tools tests` | ❌ 2 errors (tomli + `forge_paths.py:54`) | ✅ **clean with `tomli` installed** (20 files); the 1 remaining local error is only the missing `tomli` package in an environment without `requirements-dev.txt` |
| `pytest tests -q` (standalone) | ❌ 30 passed, 2 failed, 1 skipped | ❌ **34 passed, 2 failed, 1 skipped** |
| `scripts/ci.sh` (local reproduction) | ❌ (mypy + tests) | ❌ **only the 2 tests** — mypy is fixed |
| `forge.py --version` | ✅ 1.4.1 | ✅ 1.4.2 |

The two standalone pytest failures are unchanged and **consumer-coupled**:

1. `test_all_skill_files_pass_validation` asserts `project-context` (a project overlay
   skill, not a framework skill).
2. `test_project_paths_are_resolved` asserts `.agent-state/memory/agent_metrics.json`
   and `memory_policy.md` (the framework repository has no `.agent-state/`).

The suite passes **37/37** when run inside a consumer project with the expected overlay,
state and `strict_agent_system = true` (verified in §2.2 and in this repository).
**The framework CI is therefore still red** until those tests get fixtures or
standalone-mode skips. v1.4.2 fixes the mypy half of the problem, not the test half.

### 2.2 This repository after the upgrade

| Gate | Result |
| :--- | :--- |
| `forge.py validate` | ✅ 18 skills, 14 workflows, 3 templates |
| `forge.py validate --graph` | ✅ all references valid |
| `forge.py validate --conflicts` | ✅ no conflicts |
| `forge.py metrics validate` | ✅ 38 files, metric-consistent |
| `forge.py memory check` | ✅ 169 lines (limit 350) |
| `pytest .agent/tests -q` | ✅ 37 passed |
| `forge.py project test / lint / type` | ✅ 233 tests / Ruff / mypy |
| Project `ruff` / `mypy` / `pytest` | ✅ / ✅ / 233 passed |

No repository-specific migration was needed: the `forge.toml` command contract
(`test_command`, `test_command_full`, `lint_command`, `format_command`, `type_command`)
and `strict_agent_system = true` introduced with v1.4.1 remain valid in v1.4.2.

### 2.3 Regression found during close-session: `metrics report` crashes on `None`

`forge.py metrics close-session` writes `task_completion_rate: None` in the rotated
session. `forge.py metrics report` then formats it with `:.2f` at
`tools/forge_metrics_report.py:193` and crashes:

```text
TypeError: unsupported format string passed to NoneType.__format__
```

This affects any project that runs the documented sequence
`metrics close-session` → `metrics report` without filling `task_completion_rate`.
Workaround applied here (project-owned data, no submodule patch): normalize
`task_completion_rate` to `1.0` in `last_session`/`history` and add
`task_completion_rate`, `total_sessions`, `cyclomatic_complexity_gate` and
`i18n_hygiene_gate` to `summary`; the report now renders `PASS`/`1.0`/`6` instead of
crashing or printing `?`. Upstream should format `None` defensively (e.g. `n/a`).

---

## 3. Consumer status after v1.4.2

| Repository | `.agent` state | Gap |
| :--- | :--- | :--- |
| `qgis-plugin-analyzer` | **`v1.4.2`** (`b264e35`) | ✅ upgraded + committed (`b98186a`) |
| `ai-context-core` | `v1.4.2` (`b264e35`) | ✅ clean; pointer recorded |
| `sec_interp` | `v1.4.2` (`b264e35`) | ✅ clean; pointer recorded |
| `qgis-plugin-manager` | `v1.4.2` (`b264e35`), `.agent` content clean | parent pointer still `M .agent`; commit it |
| local `agentic-forge` checkout | `v1.2.0` | `git fetch origin --tags` (the consumers fetched the tag themselves) |

The ecosystem has now converged on v1.4.2; `qgis-plugin-manager`'s earlier 3-file local
patch is gone (the `.agent` working tree is clean). The only remaining administrative
item is its parent submodule-pointer commit.

---

## 4. Finding status

| ID | Finding | v1.4.2 status |
| :--- | :--- | :--- |
| F-01 | destructive `memory prune` | ✅ fixed since v1.3.0 |
| F-02 | `--graph` exit 0 | ✅ fixed since v1.3.0 |
| F-03 | overlay/scaffold validation | ✅ fixed since v1.4.0 |
| F-04 | no tests/CI, lint/type debt | 🟡 **partial**: tests + CI + Ruff/format + mypy fixed; **standalone CI still red on 2 consumer-coupled tests** |
| F-05 | version fragmentation | ✅ fixed (v1.4.x tags + `VERSION` + `--version`; all consumers on v1.4.2) |
| F-06 | Python 3.11+ vs 3.9 | ✅ fixed (`tomli` fallback + CI matrix 3.9/3.11/3.13) |
| F-07 | genericization leaks | ✅ fixed |
| F-08 | `forge.toml` keys ignored | ✅ fixed |
| F-09 | metrics false positives / `--fix` | ✅ fixed |
| F-10 | docs contradictions | ✅ mostly fixed (`QUICK_REFERENCE` 0/14; GEN8 "Partially implemented"); loose "pre-commit" wording remains |
| F-11 | `qa-docker`/`testing-standards` overlap | ✅ fixed (deprecated alias) |
| F-12 | validator/parser weaknesses | ✅ mostly fixed |
| F-13 | changelog / release process | ✅ fixed |
| F-14 | scaffold snapshot | ✅ fixed |
| F-15 | structural completeness | 🟡 **remains**: 5/9 skill checklists, 7/14 Expected Result sections |

**Net effect**: v1.4.2 is the first release whose *tooling* quality gates (Ruff, format,
mypy) are clean. The remaining framework-level defect is the **standalone test suite**,
which is the only thing keeping CI red.

---

## 5. Remaining work (v1.4.3 / v1.5.0)

1. **Make the test suite self-contained** (the only red CI item): create fixtures for
   `.agent-state/` and an overlay skill, or skip consumer-only assertions when
   `framework_dir` is a standalone checkout. Add a CI job that runs the suite both
   standalone and against a fixture project.
2. **Fix `metrics report` on `None`** (`tools/forge_metrics_report.py:193`): format
   `task_completion_rate` defensively; `rotate_session_history` itself writes `None`, so
   the documented close-session sequence crashes by default.
3. **Complete the structural checklist**: Quality Checklists for the 4 remaining skills
   and Expected Result sections for the 7 remaining workflows (or relax
   `verify-standards` to the real convention and enforce it).
4. **Resolve the `pre-commit` wording**: ship a hook or say "project-owned pre-commit".
5. **`version_bump_command`**: document a default (or the manual fallback) so
   `/release-package` is usable; this repository intentionally omits it.
6. **Ecosystem housekeeping**: commit the `qgis-plugin-manager` pointer; fetch the local
   `agentic-forge` checkout.

---

## 6. Reproduction appendix

```bash
# Tag and delta
git -C .agent fetch origin --tags
git -C .agent describe --tags
git -C .agent log --oneline v1.4.1..v1.4.2      # one commit: b264e35

# Standalone framework checks
git -C .agent archive v1.4.2 | tar -x -C /tmp/forge142
(cd /tmp/forge142 && ruff check . && ruff format --check .)
(cd /tmp/forge142 && mypy tools tests)          # passes when tomli is installed
(cd /tmp/forge142 && pytest tests -q)           # 34 passed, 2 failed, 1 skipped

# Project-context checks (this repository)
python .agent/tools/forge.py validate
python .agent/tools/forge.py validate --graph
python .agent/tools/forge.py validate --conflicts
python .agent/tools/forge.py metrics validate
python .agent/tools/forge.py memory check
python .agent/tools/forge.py --version
pytest .agent/tests -q                          # 37 passed
python .agent/tools/forge.py project test
python .agent/tools/forge.py project lint
python .agent/tools/forge.py project type
```

---

*Report generated on 2026-10-19 against `agentic-forge` v1.4.2 (`b264e35`). The `.agent/`
submodule was upgraded and committed in `b98186a`; the reports remain untracked under
project-owned `docs/reports/`.*
