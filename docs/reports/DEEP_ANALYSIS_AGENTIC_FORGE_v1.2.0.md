# Deep Analysis — Agentic Forge (`v1.2.0`) and Multi-Repository Consumption

**Framework under analysis**: `agentic-forge`, mounted as the `.agent/` git submodule.

**Pinned revision**: `v1.2.0` — commit `2de22cf579d8494da1b5ed786d24be45fe7b0c2c`.

**Upstream checkout**: `/home/jmbernales/qgispluginsdev/agentic-forge` (local clone,
`origin` = `https://codeberg.org/geociencio/agentic-forge.git`).

**Consumers audited**: `qgis-plugin-analyzer` (this repository), `ai-context-core`,
`qgis-plugin-manager`, `sec_interp`.

**Analysis date**: 2026-10-19.

> **Update (2026-10-19)**: `agentic-forge` has advanced to **v1.4.2** (`b264e35`),
> which supersedes the v1.3.0/v1.4.x intermediate fixes and closes most findings in this
> report. This document is the **v1.2.0 baseline analysis**; for the current release
> status, the fixed/remaining delta and the applied upgrade, see
> [AGENTIC_FORGE_v1.4.2_UPDATE.md](AGENTIC_FORGE_v1.4.2_UPDATE.md) (intermediate:
> [v1.4.1](AGENTIC_FORGE_v1.4.1_UPDATE.md), [v1.3.0](AGENTIC_FORGE_v1.3.0_UPDATE.md)).

**Method** (read-only; no framework or consumer file was modified):

| Tool / technique | Purpose |
| :--- | :--- |
| `git log`, `git submodule status`, `git ls-tree` | reconstruct each consumer's effective framework revision |
| `diff -rq` between `.agent` trees | quantify framework drift across consumers |
| `forge.py validate`, `--graph`, `--conflicts`, `metrics validate/report` | exercise the framework's own gates |
| `ruff` / `ruff format` / `mypy` on `.agent/tools` | framework self-quality (its own CI runs none of these) |
| Temporary project copies under `/tmp` | prove validator exit codes, overlay coverage and prune behavior |
| Synthetic `AGENT_LESSONS.md` + snapshots | prove `memory prune` data-loss semantics |

---

## 1. Executive summary

Agentic Forge is a **good idea with a weak release discipline**. The design is coherent —
framework content is versioned separately from project state, skills are described for
semantic injection, domain packs are isolated under `scaffold/`, and a single `forge.py`
CLI fronts validation, metrics, memory and lessons. The documentation is unusually rich
for a framework of this size.

However, the framework is **not currently operated as a shared dependency**:

1. **There is no released version newer than `v1.2.0`**, yet consumers already run three
   different unreleased lines of it (a local `v1.3.0` branch, remote `main` +4 commits,
   and a 25-file uncommitted patch). The canonical checkout is itself stale.
2. **`forge.py memory prune` is destructive by default** (rewrites lessons, deletes
   snapshots) while the framework, the close-session workflow and this repository's
   `AGENTS.md` advertise it as a dry-run.
3. **`forge.py validate --graph` exits `0` even when it prints broken references**, while
   `verify-standards.md` explicitly promises exit code 1. The reference-integrity gate
   cannot block anything in `v1.2.0`.
4. **The framework does not apply its own quality gates**: 19 Ruff findings, 6 mypy
   errors, 3 unformatted files, **zero tests, zero CI**.
5. **The two newest framework fixes live in consumer working trees**: overlay-workflow
   validation (in `sec_interp`) and metrics/memory gate fixes (in `ai-context-core`),
   neither available to `qgis-plugin-analyzer` on `v1.2.0`.

**Overall grade: B−.** Excellent structure and documentation; release engineering,
self-testing and cross-repository governance are the weak points.

> **Immediate operational warning for this repository**: do **not** run
> `python .agent/tools/forge.py memory prune` on the strength of the `(dry-run)` comment
> in `AGENTS.md`. On `v1.2.0` it applies the prune. Today it happens to be a no-op here
> (no `consolidated_in` lessons and no snapshots older than 90 days), but that is luck,
> not safety. Use `git status`/a backup before running it, or upgrade to a framework
> version with `--apply`.

---

## 2. Framework inventory (`v1.2.0`)

| Dimension | Content |
| :--- | ---: |
| Tracked files | 46 |
| Core skills | 9 (`agentic-memory`, `changelog-generator`, `coding-standards`, `commit-standards`, `documentation-standards`, `i18n-standards`, `qa-docker`, `release-management`, `testing-standards`) |
| Core workflows | 14 (plus `index.md`) |
| QGIS domain pack | 3 skills, 3 workflows, 1 resource |
| Tooling | 6 modules, **1,855 LOC** (`forge.py`, `forge_paths.py`, `forge_metrics.py`, `memory_prune.py`, `lesson_extractor.py`, `validate_agent_system.py`) |
| Tests | **0** |
| CI configuration | **0** |
| CHANGELOG | **absent** in `v1.2.0` |
| Architecture docs | 3 (`IMPROVEMENT_PLAN.md`, `GEN7`, `GEN8`), all written for SecInterp |
| License | MIT |
| Python requirement | implicitly **3.11+** (`tomllib` in `forge_paths.py:18`) |
| Version exposure | manual text in README/QUICK_REFERENCE ("System Version 1.2"); no `--version` command, no version constant |

Tooling size distribution:

| Module | LOC | Role |
| :--- | ---: | :--- |
| `forge_metrics.py` | 705 | metrics schema checks, trend report, session rotation |
| `validate_agent_system.py` | 603 | frontmatter, references, graph, conflicts |
| `lesson_extractor.py` | 213 | propose lessons from `git diff --stat` |
| `memory_prune.py` | 184 | prune lessons and snapshots |
| `forge_paths.py` | 82 | resolve `forge.toml`, framework/state paths |
| `forge.py` | 68 | CLI dispatcher |

---

## 3. Cross-repository consumption matrix

| Repository | Recorded gitlink | Checked-out `.agent` | Effective framework | Overlays | `forge.toml` extras | `validate` output | Working tree |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `qgis-plugin-analyzer` | `2de22cf` | `2de22cf` | **v1.2.0** | 6 skills, 0 workflows | — | 15 skills, 14 workflows | clean |
| `ai-context-core` | `2de22cf` | **`d240b54`** | v1.2.0 + local `fix/p0-quality-gates` ("v1.3.0") | 6 skills, 0 workflows | — | 15 skills, 14 workflows | parent: `M .agent` (pointer drift) |
| `qgis-plugin-manager` | `2de22cf` | `2de22cf` | **v1.2.0 + 25 uncommitted files** | 2 skills, 0 workflows (+ project `scaffold/`) | `max_cc=10`, `max_lesson_lines=350`, `strict_agent_system=true`, `test_command*`, `lint_command` | 19 skills, 14 workflows, 6 templates | parent: `m .agent` + many modified files |
| `sec_interp` | `f15d44a` | `f15d44a` | **v1.2.0 + 4 commits** (`origin/main`) | 5 skills, 4 workflows | `max_cc=10`, `test_command`, `test_command_docker` | 14 skills, 18 workflows | clean |

### 3.1 Divergence map

```text
                         (no v1.3.0 tag exists)
                                  │
  v1.2.0  2de22cf ──┬── qgis-plugin-analyzer   (pinned; clean)
   (tag)            ├── qgis-plugin-manager    (+25 uncommitted files in the submodule)
                    ├── ai-context-core        → d240b54  "fix: … (v1.3.0)"  [local branch only]
                    └── origin/main ──────────→ f15d44a  (+4 commits: overlay validation,
                                                          memory budget, unittest docs,
                                                          QGIS release count)  ← sec_interp

  Local agentic-forge checkout: still at 2de22cf; its origin/main ref has NOT fetched f15d44a.
```

**Consequences**

- **No consumer runs a released framework version newer than `v1.2.0`.** The two fixes
  that matter most operationally exist only in consumer checkouts:
  - `f15d44a` (sec_interp): validates/graphs **overlay workflows** in
    `.agent-state/workflows/` and adds memory line-budget checks.
  - `d240b54` (ai-context-core, local only): makes `--graph` fail correctly, excludes
    `scaffold/` from metric ground-truth checks, makes `memory prune` dry-run by default,
    and parameterizes the CC guidance via `[project].max_cc`.
- **The canonical repository is behind its own remote.** A developer updating
  `agentic-forge` from the local checkout would not see the sec_interp fixes without a
  fetch.
- **`qgis-plugin-manager` is maintaining a 1,033-insertion / 1,416-deletion fork** of the
  framework as uncommitted changes (tools, workflows, scaffold, docs). A
  `git submodule update` or a careless commit can lose or freeze that work.
- **Upgrade cost is now non-trivial** for every consumer: merge three divergent lines
  (`f15d44a`, `d240b54`, qpm's patch), reconcile overlapping tool changes
  (`validate_agent_system.py` touched by all three), and re-run validators.

### 3.2 Consumer-specific observations

- **`qgis-plugin-manager`** is effectively running the *future* framework: its modified
  `forge_paths.py` reads `strict_agent_system`, `max_lesson_lines`, `test_command`,
  `test_command_full`, `lint_command`; its modified validator counts project-level
  `scaffold/` packs (19 skills / 6 templates output). None of that is in `v1.2.0`. Its
  `forge.toml` therefore advertises a contract that the pinned framework cannot honor.
- **`ai-context-core`** declares `requires-python = ">=3.9"` but its `.agent` tooling
  imports `tomllib`; the framework's own unreleased CHANGELOG lists this exact
  incompatibility as a known follow-up.
- **`sec_interp`** is the only consumer whose submodule is both clean and ahead of the
  tag, and the only one that keeps **agentic tests** (`tests/agentic/`, 6 modules:
  `test_memory_prune`, `test_validate_agent_metrics`, `test_check_skill_conflicts`,
  `test_sync_metrics`, `test_overlay_workflows`, `test_release_workflow`). Those tests
  were never extracted into the framework — they test a newer API than `v1.2.0` offers.

---

## 4. Framework self-quality (the gates it preaches)

### 4.1 Own validation

| Check | Result |
| :--- | :--- |
| `forge.py validate` (this repo) | ✅ 15 skills, 14 workflows |
| `forge.py validate --conflicts` | ✅ no name/description conflicts |
| `forge.py validate --graph` | ⚠️ prints broken refs but **exits 0** (see F-02) |
| `forge.py metrics validate` (this repo) | ❌ 5 "inconsistencies", 4 of them from `scaffold/` templates (see F-09) |
| `forge.py metrics report --compact` | ⚠️ renders `?` for CC gate, i18n gate, task completion and sessions (schema mismatch) |
| `forge.py lesson propose` | ⚠️ no signals found; reads `git diff --stat`, not the patch (see F-12) |

### 4.2 External lint / typing / tests

| Gate | Command | Result |
| :--- | :--- | :--- |
| Lint | `ruff check .agent/tools --isolated --select E,F,I,UP,B` | ❌ **19 findings** (E501 ×9, F402 ×3, UP045 ×3, B007 ×1, F401 ×1, F541 ×1, I001 ×1) |
| Format | `ruff format --check .agent/tools` | ❌ 3 of 6 files would be reformatted |
| Types | `mypy .agent/tools` | ❌ **6 errors** in 3 files |
| Tests | — | ❌ none in the framework |
| CI | — | ❌ no workflow in `agentic-forge` |

Representative defects: duplicated/shadowed imports and duplicate module constants in
`validate_agent_system.py` (`from dataclasses import dataclass, field` alongside
`dc`/`dc_field`; `SCRIPTS_DIR` defined twice at lines 26 and 241), an unused `field`
shadowed by a loop variable, and untyped containers that break mypy.

### 4.3 Structural completeness vs its own `verify-standards` criteria

`workflows/verify-standards.md` asks: *"Do all Skills have a Quality Checklist?"* and
*"Do Workflows have Expected Result sections?"*. Measured on `v1.2.0`:

| Criterion | Result |
| :--- | :--- |
| Core skills with a Quality Checklist | **5 / 9** (missing: `agentic-memory`, `changelog-generator`, `documentation-standards`, `i18n-standards`) |
| Core skills with "When to use" + "Degree of Freedom" | **5 / 9** |
| Workflows with a `## Expected Result` section | **6 / 14** |
| `QUICK_REFERENCE.md` skill lists matching workflow frontmatter | **7 / 14 OK**, **7 mismatched** (see F-10) |

---

## 5. Findings

Severity: **P1** = correctness/safety/governance blocker for shared use, **P2** =
portability or contract drift, **P3** = documentation/hygiene.

### F-01 — P1 — `memory prune` is destructive by default, but documented as a dry-run

**Evidence**

- `memory_prune.main()` calls `prune_lessons()` and `prune_next_steps_snapshots()`
  unconditionally (`memory_prune.py:178-180`).
- `prune_lessons()` rewrites `AGENT_LESSONS.md` (`memory_prune.py:142`).
- `prune_next_steps_snapshots()` calls `path.unlink()` (`memory_prune.py:168`).
- There is no `--apply`, no `--dry-run`, no confirmation.
- `close-session.md:101` and `workflows/index.md:29` tell agents to run it during session
  close.
- `qgis-plugin-analyzer/AGENTS.md:217` explicitly labels it **"(dry-run)"**.
- The unreleased `v1.3.0` CHANGELOG in `ai-context-core` lists "dry-run by default; pass
  `--apply`" as a fix, confirming the defect.

**Proof** (temporary project, synthetic data): a lesson dated `2025-01-01` with
`consolidated_in` and a `next_steps_2024-01-01.md` snapshot were removed by a single
`forge.py memory prune`, exit `0`.

**Impact**: following the documented close-session flow can delete architectural history
and lessons. The current `qgis-plugin-analyzer` state is not yet exposed (no
`consolidated_in` lessons; snapshots are recent), but the behavior is a data-loss trap.

**Recommendation**: make pruning dry-run by default (`--apply` to mutate), require an
explicit confirmation, print a diff, and update every workflow/doc. Add tests equivalent
to sec_interp's `tests/agentic/test_memory_prune.py`, adapted to the new contract.

---

### F-02 — P1 — `validate --graph` always exits 0, so the integrity gate cannot fail

**Evidence**

- `graph_main()` only calls `sys.exit(1)` inside `if validate_only:` (i.e. when
  `--validate` or `--json` is present) — `validate_agent_system.py:482-490`.
- `verify-standards.md` states: *"`--graph` exits with code 1 if any workflow references a
  missing skill or script."*
- The `v1.3.0` CHANGELOG in `ai-context-core` lists this exact bug as fixed there.

**Proof** (temporary copy with a workflow referencing a missing skill and a missing
script):

```
$ forge.py validate --graph
## ❌ Broken References
  broken.md [skill]  → 'does-not-exist' NOT FOUND
  broken.md [script] → 'missing_script.py' NOT FOUND
- **Broken references**: 2
$ echo $?
0
```

With `--graph --validate` the exit code is 1 (the gate exists but is not the documented
invocation).

**Impact**: every consumer's `/verify-standards` and `/start-session` integrity check
passes even with broken skill/script references. This is the framework's most important
correctness gate and it is effectively disabled by default.

**Recommendation**: make `--graph` exit 1 on broken refs (keep `--report`/`--json` for
advisory output), and add a regression test.

---

### F-03 — P1 — Overlay workflows and scaffold references are not validated

**Evidence**

- `validate_workflows()` and `scan_workflows()` iterate only `WORKFLOW_DIR`
  (`.agent/workflows`, `validate_agent_system.py:150,337`). `forge_paths.WORKFLOW_DIR`
  points exclusively at the framework (`forge_paths.py:51`).
- `sec_interp` had to add `f15d44a` ("include overlay workflows in validate and graph") to
  cover `.agent-state/workflows/`.
- The scaffold is never scanned: `project-context` is referenced by
  `scaffold/qgis/workflows/audit-plugin.md:4` but does not exist in the framework or the
  domain pack (it is a project-specific overlay skill).
- In a probe, a broken overlay workflow (`.agent-state/workflows/overlay-broken.md`
  referencing `also-missing`) was ignored: validator reported "9 skills, 14 workflows",
  exit 0.

**Impact**: the exact place where projects extend the framework with the most
project-specific (and most error-prone) skills/workflows is the least validated. A fresh
consumer copying the QGIS pack immediately inherits a dangling `project-context`
reference.

**Recommendation**: validate framework + overlay + project `scaffold/` roots, with
templates checked for placeholder-only references; report overlay workflow counts
separately (as sec_interp's version does).

---

### F-04 — P1 — The framework has no tests and no CI, and fails its own lint/type bar

**Evidence**: 0 tests, 0 workflows in `agentic-forge`; 19 Ruff findings, 3 unformatted
files, 6 mypy errors (§4.2). The only tests for the tools live in a consumer
(`sec_interp/tests/agentic/`), and one of them (`test_overlay_workflows.py`) targets an
API that does not exist in `v1.2.0`.

**Impact**: regressions in the pieces every sibling depends on (validator, prune, metrics)
are only caught manually, and the framework that mandates `ruff`/`mypy`/`pytest` for
consumers does not run them on itself. This is the root cause that allowed F-01/F-02 to
ship in a tag.

**Recommendation**: add a minimal CI (`ruff check`, `ruff format --check`, `mypy`,
`pytest`) and move/port the six agentic test modules from `sec_interp`. At minimum, test
the validator exit codes, prune dry-run, overlay roots and metrics schema.

---

### F-05 — P1 — Four effective framework versions, no release process

**Evidence** (§3): `v1.2.0` (tag), `v1.2.0 + 4` (`origin/main`), `v1.2.0 + 1` on a local
feature branch labelled "v1.3.0", and `v1.2.0 + 25 uncommitted files`. There is no
CHANGELOG in `v1.2.0`, no `v1.3.0` tag, no release workflow, and no `forge.py --version`.

**Impact**: "what version of the framework does a repo use?" is only answerable via
`git describe` in the submodule; the same framework behaves differently in each sibling.
Bug reports and fixes cannot be matched to versions, and a fix applied in one consumer is
invisible to the others.

**Recommendation**: land `f15d44a` + `d240b54` + the qpm patch on upstream `main`, resolve
the overlapping `validate_agent_system.py` changes in one PR, add a CHANGELOG and tag
`v1.3.0`, then bump every consumer submodule pointer in a dedicated commit. Add
`forge.py --version` (read a single `__version__` constant).

---

### F-06 — P1 — Tooling requires Python 3.11+, but a consumer supports 3.9

**Evidence**: `forge_paths.py:18` imports `tomllib` (3.11+) with no `tomli` fallback;
`ai-context-core/pyproject.toml:6` declares `requires-python = ">=3.9"`. The unreleased
`v1.3.0` CHANGELOG explicitly lists this as a known follow-up. The framework README never
states the Python requirement.

**Impact**: `python .agent/tools/forge.py ...` fails with `ModuleNotFoundError` in 3.9/3.10
environments; `ai-context-core`'s documented session commands cannot run under its own
declared minimum.

**Recommendation**: either add `tomli` as a fallback and support 3.9+, or declare
"tooling requires Python 3.11+" in the README and in `forge.toml` validation (fail with a
clear message). Do not leave it implicit.

---

### F-07 — P2 — Genericization is incomplete; reference-project details remain in the core

The `v1.2.0` extraction moved QGIS *skills* to `scaffold/qgis`, but the core still carries
SecInterp/QGIS assumptions:

| Location | Leak |
| :--- | :--- |
| `skills/documentation-standards/SKILL.md:22` | hardcodes `763/763 OK` (SecInterp test count) |
| `skills/documentation-standards/SKILL.md:28`, `workflows/close-phase.md:100` | `docs/source/MAINTENANCE_LOG.md` — only exists in `sec_interp` |
| `skills/agentic-memory/SKILL.md` | "Core/GUI separation" self-audit, "Geometry Mocking" example |
| `skills/qa-docker/SKILL.md` | `FORCE_MOCKS`, `make docker-test`, geometry/UI mocks |
| `tools/forge_metrics.py:227,381-385,412-425` | `i18n_issues_qgis_analyzer`, `ground_truth_sources.qgis_analyzer` |
| `tools/lesson_extractor.py:156-157` | hardcoded `qgis-analyzer` actions and `MISSING_I18N` |
| `tools/forge_metrics.py:310-321` | `STALE_MAPPINGS` / `ARCHAIC_MARKERS` tuned to reference-project values |
| `architecture/*.md` | "SecInterp Agentic System" plans, 34 scripts / 25 tests baseline |

`QUICK_REFERENCE.md` also says the reference project adds `project-context` and
`geological-logic` — accurate for SecInterp, confusing for every other consumer.

**Impact**: a non-QGIS consumer inherits documentation and tooling that references paths,
metrics and concepts it does not have; the QGIS consumer inherits SecInterp-specific
values. The framework is generic at the directory level but not at the content level.

**Recommendation**: move every reference-project detail to `scaffold/qgis` or to
consumer overlays; replace hardcoded counts/paths with placeholders or `forge.toml`
values; make `forge_metrics` consume a project-provided adapter and a documented schema.

---

### F-08 — P2 — `forge.toml` keys used by consumers are ignored by `v1.2.0`

`qgis-plugin-manager` declares `test_command`, `test_command_full`, `lint_command`,
`strict_agent_system`, `max_lesson_lines`; `sec_interp` declares `test_command` and
`test_command_docker`. In `v1.2.0`, only `[project].max_cc` and `module_size_limit` are
read (`forge_paths.py:47-48`); the rest are silently ignored.

**Impact**: the same `forge.toml` means different things depending on which consumer's
submodule commit is checked out. A project that "opts into strict validation" gets no
strictness on `v1.2.0`; documented commands are not executed by the framework.

**Recommendation**: define and document the full `forge.toml` schema (with defaults) in
one place, validate unknown/unsupported keys with a warning, and ship the key support
together with the docs. Never let a consumer's config reference a key the pinned
framework cannot honor.

---

### F-09 — P2 — `metrics validate` produces false positives and `--fix` can corrupt docs

**Evidence** (this repository):

```
🔍 Scanned 45 agentic files (framework + state)
❌ Found 5 metric inconsistencies:
  .agent/scaffold/qgis/workflows/release-plugin.md:6   [cc_threshold] found=10 expected=15
  .agent/scaffold/qgis/workflows/release-plugin.md:11  [test_count]   found=763 expected=233
  .agent/scaffold/qgis/workflows/release-plugin.md:12  [cc_threshold] found=10 expected=15
  .agent/scaffold/qgis/workflows/release-plugin.md:29  [cc_threshold] found=10 expected=15
  .agent/skills/coding-standards/SKILL.md:54           [cc_threshold] found=10 expected=15
```

Four are domain-pack templates, one is generic guidance hardcoding CC 10. The
unreleased `v1.3.0` fixes both (exclude `scaffold/`, read `[project].max_cc`).

Additional risks:

- `should_skip_file` skips `history/` and `architecture/` but **not** `scaffold/`
  (`forge_metrics.py:470-485`).
- `auto_fix` replaces the **first textual occurrence of the number anywhere in the file**
  (`forge_metrics.py:591-620`), not the matched metric line, and `STALE_MAPPINGS` contains
  reference-project values (e.g. `cc_threshold: 15 → 10`). A match can therefore rewrite
  an unrelated version string or code sample that happens to share the same number.
- The metrics JSON schema is not versioned consistently across consumers
  (`version` vs `schema_version`, `sessions` vs `history`, missing
  `cyclomatic_complexity_gate`/`i18n_hygiene_gate`/`total_sessions`), so the report
  silently prints `?`.

**Impact**: the session workflow (`/start-session`, `/close-session`) reports failures
that are not real, and the "fix" path is unsafe for generic use. Repeated false positives
train agents to ignore the gate — the worst outcome for a quality tool.

**Recommendation**: exclude `scaffold/` and treat templates as non-ground-truth; support
project-supplied regex/mappings or disable `--fix` for unknown projects; version the
metrics schema and validate it on load; make the report fail loudly on missing keys
instead of printing `?`.

---

### F-10 — P2 — Documentation contradicts behavior and itself

| Claim | Reality |
| :--- | :--- |
| `README.md:17`: "a `pre-push` hook enforces complexity and style standards" | No hook ships in the framework; this repository has no `.git/hooks/pre-push`. |
| `verify-standards.md`: "`--graph` exits with code 1" | It exits 0 (F-02). |
| `QUICK_REFERENCE.md` skill columns | 7 of 14 workflows list a different skill set than their frontmatter (e.g. `/close-session` lists 2 of its 5 skills, `/release-package` lists 1 of 3, `/verify-standards` lists 1 of 3). |
| `IMPROVEMENT_PLAN_GEN8.md:4`: "✅ Implemented (Phases A–E complete)" | All **18** checkboxes in the same document are unchecked. |
| README: "The skill scanner validates the framework skills plus the project overlay" | True for skills, false for workflows in `v1.2.0` (F-03). |
| `AGENTS.md` (root): `memory prune ... (dry-run)` | Destructive (F-01). |
| `QUICK_REFERENCE.md`: reference project adds `project-context`/`geological-logic` | Reference-project detail in a generic document (F-07). |

**Impact**: agents follow documentation literally. Every contradiction is a potential
wrong action (deleting data, skipping a gate, loading the wrong skills).

**Recommendation**: generate the QUICK_REFERENCE skill/workflow tables from frontmatter
(the validator already parses it), fix the hook claim or ship the hook, and reconcile the
GEN8 status with its checkboxes.

---

### F-11 — P2 — `qa-docker` and `testing-standards` are near-duplicates

Both skills cover the same domain with near-identical structure: the same "When to use",
"Degree of Freedom", workflow (design → implement → execute → coverage), mocking/isolation
guidance and 80 % coverage checklist. The wording and the Docker paragraph differ, so the
duplicate-description check (`validate_agent_system.py:555-575`) reports "no conflicts"
even though a project receives overlapping, occasionally contradictory guidance depending
on which workflow it enters through.

**Impact**: workflows reference one or the other arbitrarily (`/build-feature` uses
`qa-docker`, `/audit-package` uses `testing-standards`), so agents receive different
guidance for the same activity depending on the entry point. Docker is mandatory in one
skill and optional in the other.

**Recommendation**: merge into one testing skill and move Docker specifics to
`scaffold/` (or an overlay). Extend the conflict detector to flag high textual overlap,
not just identical descriptions.

---

### F-12 — P3 — Validator/parser technical weaknesses

- **Hand-rolled YAML parser** (`parse_yaml_frontmatter`, line 58): handles only flat
  `key: value` and inline `[a, b]` lists. Block scalars (`validation: |`), block lists
  (`stop_conditions:`) and quoted values containing `:` are misread. `release-package.md`
  uses a YAML list for `validation`, while other workflows use a block scalar — both pass
  validation, but the content is not actually checked.
- **Inconsistent skill identity**: `get_all_skills()` uses directory names (line 299) while
  `validate_skills()` uses the frontmatter `name`. A renamed skill can pass one check and
  fail the other.
- **Script references**: only `scripts/NAME.py` inside fenced `bash` blocks are checked
  (lines 183-196). `.agent/tools/forge.py`, shell scripts, `make` targets and inline
  `python -c` are invisible.
- **Duplicate constants**: `PROJECT_ROOT`, `AGENT_DIR`, `WORKFLOW_DIR`, `SKILLS_DIR`,
  `SCRIPTS_DIR` are redefined mid-module (lines 240-244), and `SCRIPTS_DIR` is
  project-specific (`PROJECT_ROOT / "scripts"`), so the framework validates a directory it
  does not own.
- **Lesson extractor reads `git diff --stat`** (`lesson_extractor.py:50-60`) and then
  regexes for code (`self.tr(`, `# no-i18n`, `raise side_effect`, metric numbers) that
  never appear in a stat summary. Only filename-based signals can fire; the other
  categories are effectively dead.
- **No `--version`**, and `forge.py` dispatches via `sys.argv` mutation/importlib, which
  makes unit testing awkward.

**Recommendation**: use a real YAML parser (PyYAML is already a dependency of
`memory_prune`) or standardize on a strict frontmatter schema; unify skill identity on
directory name; add a `[tool.forge]` command table for scripts; use `git diff <since>` for
lesson signals; add `--version`.

---

### F-13 — P3 — No framework changelog, release process or machine-readable version

`v1.2.0` has no CHANGELOG, no `v1.3.0` tag, no release workflow, and no
`__version__`/`--version`. The only changelog in the ecosystem is in
`ai-context-core/.agent/CHANGELOG.md` on an unmerged local branch.

**Impact**: consumers cannot express "requires framework >= 1.3", and the release
announcement is a chat message rather than an artifact.

**Recommendation**: adopt Keep-a-Changelog, tag releases, add `forge.py --version`, and
document a submodule upgrade procedure (fetch → diff → validate → commit pointer).

---

### F-14 — P2 — The QGIS domain pack is a SecInterp snapshot, not a template

- `scaffold/qgis/skills/qgis-migration-4x/SKILL.md:8` — "prepare the **SecInterp** code".
- `scaffold/qgis/skills/ui-framework/SKILL.md:3` — "the custom **SecInterp** interface".
- `scaffold/qgis/workflows/release-plugin.md:19` — "official release of the **SecInterp** plugin"; lines 11/92 require **763 tests**; lines 6/12/29 require **CC ≤ 10**.
- `scaffold/qgis/workflows/run-tests-in-qgis.md:55,61` — `/path/to/sec_interp`, "Ran **640** tests".
- `scaffold/qgis/workflows/audit-plugin.md:2` — "qgis-plugin-analyzer **v1.9.0+**" (current is 1.16.0); line 4 references the unknown `project-context` skill.
- `sec_interp` itself updated the copy to 792 tests (`96a70d9`), proving the value is
  project-specific, not a template constant.

**Impact**: a new consumer that copies the pack inherits another project's test counts,
path and project name, and a dangling skill reference. `metrics validate` then fails on
those constants (F-09).

**Recommendation**: convert the pack to placeholders (`<TEST_COUNT>`, `<PROJECT_NAME>`,
`<MAX_CC>`) with a short "fill these" checklist, remove the `project-context` reference
(or document it as an overlay prerequisite), and update the analyzer version constraint to
a range.

---

### F-15 — P3 — Structural completeness does not meet the framework's own audit criteria

Only 5/9 core skills have a Quality Checklist and 6/14 workflows have an Expected Result
section, while `verify-standards.md` explicitly checks both. Either the criteria or the
content should change.

**Recommendation**: add the missing sections (small effort), or relax `verify-standards`
to the actual convention and make the validator enforce the chosen convention.

---

## 6. What the framework gets right

- **Clean state boundary**: `.agent/` (framework) vs `.agent-state/` (project). The skills
  repeatedly instruct agents never to write project memory into the framework or scaffold
  (`agentic-memory` "Verify Path"; `forge_paths` separates `STATE_DIR`).
- **Single CLI**: `forge.py` is a small, readable dispatcher; subcommands are discoverable.
- **Useful validation surface**: frontmatter, skill/script references, dependency graph,
  conflict detection and a metrics consistency check — the right *ideas*, even where the
  implementation has gaps.
- **Domain-pack concept**: `scaffold/<domain>/` is the correct way to keep QGIS content
  out of the core; the extraction direction is right.
- **Rich documentation**: README, AGENTS, QUICK_REFERENCE, 14 workflows with frontmatter
  and stop conditions.
- **Zero runtime third-party dependencies** for `forge.py validate`/`memory`/`metrics`
  apart from PyYAML in `memory_prune` (which should be declared).
- **MIT license** and a clear submodule consumption model.

---

## 7. Consolidation plan

### 7.1 Immediate, safe actions (this repository)

1. **Do not run `forge.py memory prune`** until the framework is upgraded; if needed,
   snapshot `.agent-state/` first. The `(dry-run)` comment in `AGENTS.md` is wrong for
   `v1.2.0`.
2. Treat `forge.py validate --graph` as **advisory**; for a real gate run
   `forge.py validate --graph --validate` (or `--json`), which does exit non-zero.
3. Treat `forge.py metrics validate` failures as **known false positives** (already
   documented in `.agent-state/next_steps.md`), and never run `--fix` on this repo.
4. Add `i18n-maintenance` to the root `AGENTS.md` workflow table (the framework has 14
   workflows; the table lists 13).
5. When the framework cuts `v1.3.0`, upgrade the submodule pointer, add
   `test_command`/`lint_command` to `forge.toml` if the new version reads them, and
   re-run the validators.

### 7.2 Framework release work (upstream `agentic-forge`)

| # | Action | Priority |
| :--- | :--- | :---: |
| 1 | Merge `f15d44a` (overlay validation, memory budget) + `d240b54` (graph exit, metrics, prune dry-run, CC parameter) + qpm's patch; resolve `validate_agent_system.py` conflicts once | P1 |
| 2 | Make `memory prune` dry-run by default (`--apply` to mutate) and add a diff preview | P1 |
| 3 | Make `--graph` exit 1 on broken refs; keep `--json`/`--report` advisory | P1 |
| 4 | Add CI (`ruff`, `format --check`, `mypy`, `pytest`) and port `sec_interp/tests/agentic/` | P1 |
| 5 | Declare Python support; add `tomli` fallback or fail clearly on <3.11 | P1 |
| 6 | Validate overlay + project `scaffold/` roots; exclude `scaffold/` from metrics ground truth | P2 |
| 7 | Publish the `forge.toml` schema and validate unknown keys; honor `test_command`/`lint_command`/`strict_agent_system`/`max_lesson_lines` | P2 |
| 8 | Version the metrics JSON schema; stop printing `?` for missing gates | P2 |
| 9 | Genericize the remaining SecInterp/QGIS leaks; turn the QGIS pack into placeholders | P2 |
| 10 | Generate QUICK_REFERENCE tables from frontmatter; fix the pre-push claim and the GEN8 status | P2 |
| 11 | Merge `qa-docker` + `testing-standards`; extend conflict detection to textual overlap | P2 |
| 12 | Add `forge.py --version`, a CHANGELOG and a tagged `v1.3.0` release; publish the submodule bump procedure | P3 |

### 7.3 Per-consumer follow-up

| Consumer | Action |
| :--- | :--- |
| `qgis-plugin-analyzer` | Stay on `v1.2.0` until `v1.3.0`; avoid `memory prune`; run `--graph --validate`; upgrade in one commit and re-validate. |
| `ai-context-core` | Push/merge `fix/p0-quality-gates` to upstream; do not leave the submodule pointer dirty (`M .agent`). |
| `qgis-plugin-manager` | Freeze the 25-file local framework patch into a branch/PR upstream; do not keep it uncommitted in the submodule. |
| `sec_interp` | Keep the agentic tests; upstream them together with `f15d44a`; move them to the framework once it has CI. |

---

## 8. Reproduction appendix

```bash
# Revision matrix
for r in qgis-plugin-analyzer/qgis_plugin_analyzer ai-context-core qgis-plugin-manager sec_interp; do
  echo "== $r"; git -C "/home/jmbernales/qgispluginsdev/$r" submodule status
  git -C "/home/jmbernales/qgispluginsdev/$r" ls-tree HEAD .agent
done

# Framework ownership / drift
git -C .agent log --oneline v1.2.0..HEAD
git -C /home/jmbernales/qgispluginsdev/sec_interp/.agent log --oneline -6 origin/main
git -C /home/jmbernales/qgispluginsdev/ai-context-core/.agent branch -avv

# Framework self-quality
ruff check .agent/tools --isolated --select E,F,I,UP,B --line-length 100
ruff format --check .agent/tools
mypy .agent/tools

# Framework gates
python .agent/tools/forge.py validate
python .agent/tools/forge.py validate --graph          # exits 0 despite broken refs
python .agent/tools/forge.py validate --graph --validate
python .agent/tools/forge.py metrics validate          # 5 false positives
python .agent/tools/forge.py metrics report --compact
python .agent/tools/forge.py lesson propose

# Destructive-prune proof: run in a temporary project copy with an old
# consolidated lesson and an old next_steps snapshot.
python .agent/tools/forge.py memory prune
```

Evidence for the overlay gap: a temporary `.agent-state/workflows/overlay-broken.md`
referencing `also-missing` was ignored by `forge.py validate` (14 workflows reported, exit
0). Evidence for the scaffold gap: `scaffold/qgis/workflows/audit-plugin.md` references
`project-context`, which is absent from the framework and the domain pack.

---

*Report generated on 2026-10-19 against agentic-forge `v1.2.0` (`2de22cf`) and the four
consumer repositories listed above. No production file was modified; only this report was
added under project-owned `docs/reports/` (outside the `.agent/` submodule).*
