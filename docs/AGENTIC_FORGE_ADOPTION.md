# Agentic Forge Adoption — Migration Report

**Date**: 2026-10-08
**Author**: @architect (+ @qa_engineer verification)
**Scope**: Unify the agentic systems of `qgis-plugin-analyzer`, `qgis-plugin-manager`, and `ai-context-core` on the **agentic-forge** framework.

---

## 1. Context

A reevaluation of the SecInterp agentic system (2026-10-04) extracted the reusable
framework into **`agentic-forge`** (https://codeberg.org/geociencio/agentic-forge,
MIT), mounted as a git submodule at `.agent/`, with project-owned state under
`.agent-state/` and a `forge.toml` path/config contract.

The three sibling projects shared the same lineage but sat in different generations
(Gen 5 vs Gen 8) with duplicated, drifting agentic systems. This report documents
their unification on the `agentic-forge` pattern.

### Target model

```
<project>/
├── .agent/           ← git submodule → codeberg.org/geociencio/agentic-forge
│   ├── skills/       (generic)   ├── workflows/ (generic)
│   ├── tools/        (forge.py CLI + validators/pruners/metrics)
│   ├── scaffold/<domain>/        (qgis, ...)
│   └── AGENTS.md     (default config)
├── .agent-state/     ← project-owned (never overwritten by framework updates)
│   ├── memory/  task.md  next_steps.md  history/
│   └── skills/       (overlay: project-context, domain-logic, ...)
├── forge.toml        ← [forge].framework/.state + [project] thresholds
├── opencode.json     ← native subagents (allow/ask/deny) + skills.paths
└── AGENTS.md         ← canonical root override (what opencode loads)
```

---

## 2. Confirmed decisions

1. **Framework consumption = git submodule** (single source of truth, explicit
   version pinning via gitlink, `submodules: recursive` in CI).
2. **`qa-standards` → `testing-standards`**, promoted to the framework as a generic skill.
3. **`release-management` → generic (PyPI)** upstream; the QGIS variant lives in `scaffold/qgis`.
4. **Thresholds** extracted to `forge.toml` from the analyzer's own rules:
   `max_cc = 15` (`HIGH_COMPLEXITY` rule), `module_size_limit = 400` (framework default).

Minor (locked): `i18n-standards` genericized upstream (visitor notes folded into
`domain-logic`); workflow overlay support deferred; `module_size_limit` uses the
framework default.

---

## 3. Part A — Upstream genericization (`agentic-forge`)

Published as commit `2de22cf` and tag **`v1.2.0`** on Codeberg.

| Item | Change |
| :--- | :--- |
| **A2** | Moved `qgis-core`, `qgis-migration-4x`, `ui-framework` + `qgis_gold_snippets.md` → `scaffold/qgis/`. Moved QGIS workflows `audit-plugin`, `release-plugin`, `run-tests-in-qgis` → `scaffold/qgis/workflows/`. |
| **A1** | Genericized `release-management` (PyPI), `i18n-standards`, `qa-docker`; de-SecInterp-ized `coding-standards` and `agentic-memory`. |
| **A3** | Added `testing-standards` (genericized from the analyzer's `qa-standards`). |
| **A4** | Added generic workflows `release-package` (PyPI) and `audit-package` (self-audit). |
| **Workflows** | 14 generic workflows, bodies cleaned of QGIS/`qgis-analyzer`/`ai-ctx`/hardcoded test counts; no references to project scripts. |
| **Docs** | Updated `AGENTS.md`, `QUICK_REFERENCE.md`, `README.md`, `workflows/index.md`; added `scaffold/qgis/README.md`. |

**Final generic core**: 9 skills + 14 workflows. QGIS is a domain pack under `scaffold/qgis/`.

---

## 4. Part B — Migration of `qgis-plugin-analyzer`

Committed as `4b10b11`.

### F1 — State/path split
- Moved `memory/`, `history/`, `task.md`, `next_steps.md` → `.agent-state/` (`git mv`).
- Added `forge.toml`:
  ```toml
  [forge]
  framework = ".agent"
  state = ".agent-state"

  [project]
  name = "qgis-plugin-analyzer"
  test_dirs = ["tests"]
  analyzer_command = "uv run qgis-analyzer analyze . --max-cc 15"
  max_cc = 15
  module_size_limit = 400
  ```

### F2 — Content split
- Moved `domain-logic` and `project-context` → `.agent-state/skills/` (overlay).
- Folded the `I18nVisitor` heuristic notes into `domain-logic`.
- Fixed stale `project-context` (Typer → argparse, Python 3.9 → 3.11, jinja2 → dominate).

### F3 — Submodule
- `.agent/` became a git submodule of `agentic-forge`, pinned at `v1.2.0` (`2de22cf`).
- CI `release.yml`: added `submodules: recursive` to both checkout steps.

### F4 — Tooling
- Removed `scripts/{mcp_server,memory_prune,run_tests_in_qgis,security_scan,validate_agent_system}.py` and `scripts/upstream/`.
- Kept `scripts/sync_metrics.py` as the collector/adapter (repointed to `.agent-state/memory/agent_metrics.json`).

### F5 — Cleanup + docs
- Removed `.ai-context/`, `scaffold/`, `agentic_framework_guide.md`, `agentic_framework_skeleton.zip`.
- `pyproject.toml`: dropped the `ai-context-core` dev-dependency; ruff now excludes `.agent` and `.agent-state`.
- `opencode.json`: `skills.paths = [".agent/skills", ".agent-state/skills"]`.
- Rewrote root `AGENTS.md` (framework skills + overlay + `forge.py` tooling).
- Updated `.analyzerignore` and `docs/DEVELOPMENT_LOG.md`.

---

## 5. Verification (gates)

| Gate | Result |
| :--- | :--- |
| `python .agent/tools/forge.py validate` | ✅ 11 skills (9 framework + 2 overlay), 14 workflows, no broken refs |
| `python .agent/tools/forge.py validate --conflicts` | ✅ no overlaps |
| `git submodule status` | ✅ `.agent` @ `v1.2.0` |
| `uv run ruff check .` | ✅ all checks passed |
| `uv run mypy src/` | ✅ 54 source files, no issues |
| `uv run python -m pytest tests/ -q` | ✅ 126 passed |

---

## 6. Current state

- `agentic-forge`: `v1.2.0` (generic core + `scaffold/qgis`).
- `qgis-plugin-analyzer`: migrated (pilot validated).
- `qgis-plugin-manager`: **pending** (Gen 5 → Gen 8).
- `ai-context-core`: **pending** (Gen 8, no forge).

---

## 7. Next steps (Part C/D)

1. Replicate the template on `ai-context-core` (Gen 8 → forge submodule + overlay).
2. Replicate on `qgis-plugin-manager` (Gen 5 → forge, the largest lift).
3. Add a cross-repo gate confirming all three pin the same framework version.

---

## 8. References

- Framework repo: https://codeberg.org/geociencio/agentic-forge (MIT)
- Session log: `docs/maintenance/session_2026-10-08_agentic_forge_adoption.md`
- Unified plan: `docs/plans/implementation_plan_unify_agentic_systems.md` (sec_interp repo)
