# Agentic Forge v1.3.0 — Release Verification & Delta

**Release**: `v1.3.0` — annotated tag `400c530` → commit
`5bff43a820ab0cc26208e6a1d225b2be44e06adf`, dated 2026-10-18, titled
*"quality gates that enforce"*.

**Upstream**: `https://codeberg.org/geociencio/agentic-forge.git` — verified with
`git ls-remote --tags origin v1.3.0`:
`400c530… refs/tags/v1.3.0` and `5bff43a… refs/tags/v1.3.0^{}`.

**Analyzed**: 2026-10-19, by extracting the tag with `git archive` into a temporary
directory and running the framework's own gates plus isolated probes.

**Base document**: this report is the delta against
[DEEP_ANALYSIS_AGENTIC_FORGE_v1.2.0.md](DEEP_ANALYSIS_AGENTIC_FORGE_v1.2.0.md).
Findings `F-01`…`F-15` refer to that report.

> **Update (2026-10-19)**: `v1.4.1` (`537f9fd`) supersedes this release and closes most
> of the remaining findings (tests/CI, `--version`, configurable tooling, genericization,
> scaffold validation, `qa-docker` merge). This document is kept as the **v1.3.0
> intermediate delta**; for the current status and the applied upgrade, see
> [AGENTIC_FORGE_v1.4.1_UPDATE.md](AGENTIC_FORGE_v1.4.1_UPDATE.md).

> **Correction to the previous report**: the statement "no `v1.3.0` tag exists" was true
> for the local checkouts at the time of the first analysis, but is now obsolete. The tag
> exists on the remote, `ai-context-core` has already checked it out, and the upgrade is
> safe for this repository (verified in §2.3 and applied in §4.1). The stale local
> `agentic-forge` checkout simply had not fetched it.

---

## 1. What v1.3.0 contains

`v1.3.0` is `v1.2.0` + 7 commits:

```text
5bff43a docs: document v1.3.0 contents
c9958d2 docs: keep memory prune wording generic
4ec8aa0 fix: enforce validation and memory gates (v1.3.0)
f15d44a feat(validation): include overlay workflows in validate and graph
b9ba98c docs(testing): standardize workflows on unittest
45e7532 feat(memory): enforce lesson line budget and add check command
96a70d9 docs(qgis): refresh the release-plugin test count to 792
2de22cf feat: genericize framework core and extract QGIS domain pack   ← v1.2.0
```

**Fixed / added**

- `validate --graph` now exits `1` on broken references (was always `0`).
- Validation and the dependency graph include **project overlay workflows** from
  `.agent-state/workflows/`; duplicate workflow names are rejected.
- `memory prune` is **dry-run by default**; `--apply` is required to rewrite/delete.
  PyYAML is imported lazily and Markdown-bullet lessons are supported.
- New `forge.py memory check` enforces a 350-line active-lesson budget.
- `metrics validate` **excludes `scaffold/<domain>/`** from ground-truth checks.
- `coding-standards` uses `[project].max_cc` instead of hardcoding CC 10.
- `CHANGELOG.md` added; README/QUICK_REFERENCE bumped to 1.3.

**Not changed (still true in v1.3.0)**

- No tests, no CI.
- 17 Ruff findings, 4 files unformatted, 5 mypy errors.
- No `forge.py --version`; version is still manual text.
- No scaffold validation (`scaffold/qgis/workflows/audit-plugin.md` still references the
  missing `project-context` skill, and validation still ignores it).
- Python 3.11+ (`tomllib`); `ai-context-core` still declares `>=3.9`.
- `test_command` / `lint_command` / `strict_agent_system` / `max_lesson_lines` still not
  read by the framework tooling.
- Reference-project constants (`763`, `docs/source/MAINTENANCE_LOG.md`,
  `qgis_analyzer`, SecInterp) remain in core skills/workflows/tools.
- `--fix` still replaces the first textual occurrence of a number in a file.
- Metrics JSON schema is still unversioned/divergent across consumers.

---

## 2. Verification (empirical)

### 2.1 Gates on a clean v1.3.0 tree

| Check | Result |
| :--- | :--- |
| `ruff check tools --select E,F,I,UP,B` | ❌ 17 findings (E501 ×8, F402 ×3, UP045 ×3, B007 ×1, F401 ×1, F541 ×1) |
| `ruff format --check tools` | ❌ 4 of 6 files would be reformatted |
| `mypy tools` | ❌ 5 errors in 3 files |
| Tests / CI | ❌ 0 / 0 |
| `forge.py --version` | ❌ `Unknown command: --version` (exit 2) |

### 2.2 Behavior probes

| Probe | v1.2.0 | v1.3.0 |
| :--- | :--- | :--- |
| Broken refs + `validate --graph` | prints, exit **0** | prints, exit **1** ✅ |
| Overlay workflow (`.agent-state/workflows/`) with unknown skill | ignored | flagged, exit **1** ✅ |
| Duplicate workflow name (framework + overlay) | not detected | `[ERROR] Duplicate workflow name` ✅ |
| `memory prune` without flags | **deletes/rewrites** | prints "Would prune … (use --apply)", files intact ✅ |
| `memory prune --apply` | n/a | deletes/rewrites ✅ |
| `metrics validate` with `scaffold/` containing 763 tests / CC 10 | 5 false positives | **exit 0**, scaffold ignored ✅ |
| Scaffold with a broken skill ref (`project-context`) | ignored | still ignored ❌ |
| `memory check` (169-line lessons file) | n/a | `✅ 169 lines (limit 350)` ✅ |

### 2.3 Upgrade dry-run against this repository

A temporary project was built with **v1.3.0 as `.agent`**, this repository's real
`.agent-state/` (6 overlay skills, lessons, metrics) and its real `forge.toml`:

```text
forge.py validate                 → ✅ 15 skills, 14 workflows
forge.py validate --graph         → ✅ all references valid
forge.py validate --conflicts     → ✅ no conflicts
forge.py metrics validate         → ✅ 38 files, metric-consistent (the 5 v1.2.0
                                     false positives are gone)
forge.py memory check             → ✅ 169 lines (limit 350)
```

**Conclusion: the upgrade is safe for `qgis-plugin-analyzer`.** No project state or
analysis code needs to change. The `(dry-run)` comment in the root `AGENTS.md` becomes
correct, and `validate --graph` becomes a real gate instead of an advisory print.

### 2.4 Consumer status after v1.3.0

| Repository | `.agent` state | Gap |
| :--- | :--- | :--- |
| `qgis-plugin-analyzer` | **`v1.3.0`** (`5bff43a`) | ✅ upgraded in `b41facd`; all gates green |
| `ai-context-core` | `v1.3.0` (`5bff43a`) | parent still records `v1.2.0` (`M .agent`); commit the pointer |
| `qgis-plugin-manager` | `v1.2.0` + **25 uncommitted files** | local fork not upstreamed; missing all v1.3.0 fixes |
| `sec_interp` | `f15d44a` | **3 commits behind v1.3.0**; has overlay validation but not the graph/prune/metrics fixes |
| local `agentic-forge` checkout | `v1.2.0`, no fetch | `git fetch origin --tags` would show `v1.3.0` |

The tag exists now, but **two of the four consumers still do not run it**:
`qgis-plugin-manager` is on `v1.2.0`, and `sec_interp` is on a pre-tag commit.
`qgis-plugin-analyzer` was upgraded on 2026-10-19 (`b41facd`); `ai-context-core` runs the
tag but its parent repository has not committed the new pointer.

---

## 3. Finding-by-finding delta

| ID | v1.2.0 finding | v1.3.0 status | Evidence |
| :--- | :--- | :--- | :--- |
| F-01 | `memory prune` destructive by default | ✅ **Fixed** | dry-run default + `--apply`; probe left files intact |
| F-02 | `validate --graph` always exit 0 | ✅ **Fixed** | probe exits 1 on broken refs |
| F-03 | overlay/scaffold not validated | 🟡 **Partial** | overlay + duplicate names fixed; **scaffold still ignored** (`project-context` passes) |
| F-04 | no tests/CI, lint/type debt | ❌ **Remains** | 0 tests/CI; 17 lint, 5 mypy, 4 format |
| F-05 | fragmented versions, no release | 🟡 **Partial** | `v1.3.0` tag + CHANGELOG; 3/4 consumers still behind; no `--version` |
| F-06 | Python 3.11+ vs consumer 3.9 | ❌ **Remains** | `tomllib` unchanged; listed as known follow-up |
| F-07 | genericization leaks | ❌ **Remains** | `763`, `docs/source`, `qgis_analyzer`, `SecInterp` still present |
| F-08 | `forge.toml` keys ignored | ❌ **Remains** | no `test_command`/`lint_command`/`strict_agent_system` in tools |
| F-09 | metrics false positives / `--fix` risk | 🟡 **Partial** | scaffold + CC fixed; blind replace + schema divergence remain |
| F-10 | docs contradictions | ❌ **Remains** | 7/14 QUICK_REFERENCE mismatches; `pre-push` claim; GEN8 "implemented" |
| F-11 | `qa-docker`/`testing-standards` overlap | ❌ **Remains** | both skills still shipped |
| F-12 | validator/parser weaknesses | ❌ **Remains** | naive YAML parser, `git diff --stat` lessons, no `--version` |
| F-13 | no changelog / release process | 🟡 **Partial** | CHANGELOG + tag added; no release workflow/`--version` |
| F-14 | scaffold is a SecInterp snapshot | ❌ **Remains** | 763 tests, project name, `project-context` ref |
| F-15 | structural completeness | ❌ **Remains** | 5/9 skill checklists, 6/14 Expected Result sections |

**Net effect**: the two *data-safety* and *gate-integrity* defects (F-01, F-02) and the
overlay/metrics correctness issues are fixed. The **framework-engineering debt** (tests,
CI, self-lint/type, genericization, docs) is unchanged, and the *release/governance* gap
is only half-closed because the consumers have not moved to the tag.

---

## 4. Recommended actions

### 4.1 Upgrade this repository — ✅ applied (`b41facd`)

The upgrade was executed on 2026-10-19: `.agent` moved from `v1.2.0` (`2de22cf`) to
`v1.3.0` (`5bff43a`) and the pointer was committed as
`b41facd chore(agent): bump agentic-forge to v1.3.0` together with the
`next_steps.md` resolution note. Commands used (kept for reproducibility):

```bash
cd /home/jmbernales/qgispluginsdev/qgis-plugin-analyzer/qgis_plugin_analyzer

git -C .agent fetch origin --tags
git -C .agent checkout v1.3.0
git add .agent
git commit -m "chore(agent): bump agentic-forge to v1.3.0"
```

Then re-run the gates:

```bash
python .agent/tools/forge.py validate
python .agent/tools/forge.py validate --graph
python .agent/tools/forge.py validate --conflicts
python .agent/tools/forge.py metrics validate
python .agent/tools/forge.py memory check
```

Post-upgrade results (executed, not just expected):

```text
validate                  → ✅ 15 skills, 14 workflows
validate --graph          → ✅ all references valid (2 unreferenced project scripts)
validate --conflicts      → ✅ no conflicts
metrics validate          → ✅ 38 files, metric-consistent
memory check              → ✅ 169 lines (limit 350)
ruff check .              → ✅ all checks passed
mypy src/                 → ✅ 72 source files
pytest tests/ -q          → ✅ 233 passed
```

The `metrics validate` false positives documented in `.agent-state/next_steps.md` are
gone, and that "Known Issue" entry was updated to **RESOLVED** in the same commit.

> Do **not** run `memory prune --apply` unless you intend to prune; the default (no flag)
> is now a real dry-run and is safe.

### 4.2 Move the rest of the ecosystem

| Repository | Action |
| :--- | :--- |
| `ai-context-core` | Commit the submodule pointer to `5bff43a` (`M .agent` is currently uncommitted); run the v1.3.0 gates. |
| `sec_interp` | Bump `f15d44a` → `v1.3.0` to get the graph/prune/metrics fixes; keep its agentic tests and upstream them. |
| `qgis-plugin-manager` | Convert the 25-file local patch into an upstream branch/PR; do not keep it uncommitted in the submodule. Its `strict_agent_system`/project-scaffold features are not in v1.3.0. |
| local `agentic-forge` | `git fetch origin --tags` (the working checkout is still v1.2.0). |

### 4.3 Remaining framework backlog (for v1.4.0)

1. Add CI + port `sec_interp/tests/agentic/`; fix the 17 lint / 5 mypy / 4 format issues.
2. Validate project `scaffold/` references (F-03) and replace the SecInterp constants with
   placeholders (F-14).
3. Read/validate the documented `forge.toml` keys, or remove them from the docs (F-08).
4. Genericize the remaining `763`, `docs/source`, `qgis_analyzer` and SecInterp references (F-07).
5. Add `forge.py --version`, a release workflow, and a metrics schema version (F-05/F-09/F-13).
6. Reconcile `QUICK_REFERENCE` with frontmatter, fix the `pre-push` claim, and make GEN8's
   status match its checkboxes (F-10).
7. Declare Python 3.11+ or add a `tomli` fallback (F-06).
8. Merge `qa-docker`/`testing-standards` or differentiate them clearly (F-11).

---

## 5. Reproduction appendix

```bash
# Tag verification
git ls-remote --tags https://codeberg.org/geociencio/agentic-forge.git 'v1.3.0*'
git -C /home/jmbernales/qgispluginsdev/ai-context-core/.agent describe --tags
git -C /home/jmbernales/qgispluginsdev/ai-context-core/.agent log --oneline f15d44a..v1.3.0

# Extract the release without touching any checkout
git -C /home/jmbernales/qgispluginsdev/ai-context-core/.agent archive v1.3.0 \
  | tar -x -C /tmp/forge130

# Self-quality
ruff check /tmp/forge130/tools --isolated --select E,F,I,UP,B --line-length 100
ruff format --check /tmp/forge130/tools
(cd /tmp/forge130 && mypy tools)

# Behavior probes (in a temporary project with .agent + .agent-state + forge.toml)
python .agent/tools/forge.py validate
python .agent/tools/forge.py validate --graph          # exits 1 on broken refs
python .agent/tools/forge.py memory prune              # dry-run
python .agent/tools/forge.py memory prune --apply      # destructive, explicit
python .agent/tools/forge.py memory check
python .agent/tools/forge.py metrics validate          # scaffold excluded
python .agent/tools/forge.py --version                 # still unsupported
```

---

*Report generated on 2026-10-19 against `agentic-forge` v1.3.0 (`5bff43a`) and the four
consumer repositories. The `.agent/` submodule was upgraded to `v1.3.0` and committed in
`b41facd`; the reports themselves remain untracked under project-owned `docs/reports/`.*
