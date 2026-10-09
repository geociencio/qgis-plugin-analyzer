# Session 2026-10-08 — Agentic Forge Adoption (F1–F5)

**Topic**: `agentic_forge_adoption`
**Agent role**: @architect (+ @qa_engineer for verification)
**Result**: ✅ COMPLETE — qgis-plugin-analyzer now consumes `agentic-forge` `v1.2.0` as a submodule.

---

## Objective

Migrate the analyzer's Gen 8 agentic system onto the **agentic-forge** framework
(Codeberg, MIT), separating the re-usable framework (submodule at `.agent/`) from
project-owned state (`.agent-state/`). This is the pilot for unifying the three
sibling projects (`qgis-plugin-analyzer`, `qgis-plugin-manager`, `ai-context-core`).

Approved plan: `docs/plans/implementation_plan_unify_agentic_systems.md` (in the
sec_interp repo) — Part B.

---

## What was done

### Part A (upstream, done previously)
- `agentic-forge` `v1.2.0`: genericized core (9 skills + 14 workflows), QGIS domain
  extracted to `scaffold/qgis/`, added `testing-standards`, `release-package`,
  `audit-package`.

### F1 — State/path split
- Moved `memory/`, `history/`, `task.md`, `next_steps.md` → `.agent-state/` (`git mv`).
- Added `forge.toml` (`framework = ".agent"`, `state = ".agent-state"`,
  `max_cc = 15`, `module_size_limit = 400`).

### F2 — Content split
- Moved `domain-logic`, `project-context` → `.agent-state/skills/` (overlay).
- Folded the `I18nVisitor` heuristic/notes into `domain-logic`.
- Fixed stale `project-context` content (Typer → argparse, Python 3.9 → 3.11,
  jinja2 → dominate).

### F3 — Submodule
- `.agent/` converted to a git submodule of `agentic-forge`, pinned at `v1.2.0`
  (`2de22cf`).
- CI `release.yml`: `submodules: recursive` on both checkout steps.

### F4 — Tooling
- Removed `scripts/{mcp_server,memory_prune,run_tests_in_qgis,security_scan,validate_agent_system}.py`
  and `scripts/upstream/`.
- Kept `scripts/sync_metrics.py` as the collector/adapter (repointed to
  `.agent-state/memory/agent_metrics.json`).

### F5 — Cleanup + docs
- Removed `.ai-context/`, `scaffold/`, `agentic_framework_guide.md`,
  `agentic_framework_skeleton.zip`.
- `pyproject.toml`: dropped `ai-context-core` dev-dep; ruff now excludes `.agent`
  and `.agent-state`.
- `opencode.json`: `skills.paths = [".agent/skills", ".agent-state/skills"]`.
- Rewrote root `AGENTS.md` (framework skills + overlay + `forge.py` tooling).
- Updated `.analyzerignore` (`.agent-state/`, `forge.toml`, `.gitmodules`).

---

## Verification

- `python .agent/tools/forge.py validate` → 11 skills (9 framework + 2 overlay),
  14 workflows, no broken refs.
- `python .agent/tools/forge.py validate --conflicts` → no overlaps.
- `git submodule status` → `.agent` @ `v1.2.0`.
- `uv run ruff check .` → all checks passed.
- `uv run mypy src/` → 54 files, no issues.
- `uv run python -m pytest tests/ -q` → 126 passed.

---

## Commits

- `agentic-forge`: `2de22cf` (tag `v1.2.0`).
- `qgis-plugin-analyzer`: (this migration, see git log).

---

## Resume

Analyzer migration complete. Follow-ups: replicate the template on
`ai-context-core` and `qgis-plugin-manager` (Part C/D), then add a cross-repo gate
confirming all three pin the same framework version.
