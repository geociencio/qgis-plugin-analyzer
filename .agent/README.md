# qgis-plugin-analyzer Agentic System (Generation 8)

Welcome to the **qgis-plugin-analyzer Agentic Intelligence Core**. This directory contains the brain, tools, and protocols for AI-assisted development of the QGIS Plugin Analyzer.

> **⚠️ Single Source of Truth**: The canonical agent configuration is the **root `AGENTS.md`** (roles, skills matrix, workflows table), which opencode loads automatically. This `.agent/` directory holds the skills, workflows, memory, and history that the root `AGENTS.md` references. `.agent/AGENTS.md` is only a compatibility pointer — do not edit it.

## 🚀 Overview: The Generation 8 Architecture

Gen 8 drops the runtime-bridge layer and adopts **opencode-native** mechanisms only:

1. **Root `AGENTS.md` as SSoT** — no more duplicated config or `skill_sync.py` generation.
2. **Native subagents** — `architect` / `qa_engineer` / `auditor` registered inline in `opencode.json` with a permission gradient (`allow` → `ask` → `deny`).
3. **Skills discovered natively** — opencode indexes `.agent/skills` via `skills.paths`.
4. **Consolidated tooling** — one validator, one memory pruner, one metric syncer.
5. **3-tier memory** — working / episodic / semantic, with automated pruning.

## 📁 Directory Structure

```bash
.agent/
├── AGENTS.md               # ➡️ Compatibility pointer (canonical config is root AGENTS.md)
├── QUICK_REFERENCE.md      # 📋 Fast lookup for skills and workflows
├── README.md               # This file — system overview
├── next_steps.md           # 🎯 Active goals and handoff state
├── task.md                 # 📌 Active task board
├── architecture/           # 🏗️ System design and improvement plans
│   └── IMPROVEMENT_PLAN_GEN8.md  # Gen 5→8 roadmap
├── memory/                 # 🧠 Cognitive history and lessons
│   ├── AGENT_LESSONS.md    # Structured technical lessons (YAML)
│   ├── agent_metrics.json  # Operational metrics
│   └── memory_policy.md    # Memory lifecycle policy
├── skills/                 # 🛠️ On-demand capabilities (11)
├── workflows/              # 🔄 Standardized procedures (11)
│   └── index.md            # Workflow quick reference
└── history/                # 📜 Archived task boards and next_steps snapshots
    ├── tasks/              # Phase task archives
    └── next_steps/         # Session handoff snapshots (90-day retention)
```

Tooling lives in the root `scripts/` directory (not in `.agent/`):

| Script | Purpose |
| :--- | :--- |
| `scripts/validate_agent_system.py` | Validate skills/workflows/AGENTS.md consistency |
| `scripts/memory_prune.py` | Prune expired `next_steps` snapshots + report stale lessons |
| `scripts/sync_metrics.py` | Self-analysis + metrics sync to `agent_metrics.json` |

## How to Use

### Starting a Session
Always start with `/start-session`. It syncs context, reads active tasks, and validates the environment.

### Developing and Testing
Use specialized workflows like `/build-feature` or `/refactor-code`. The `/ia-critic` workflow reviews plans before implementation.

### Committing
Use `/create-commit`. Validates linting, types, and commit message format.

### Closing a Session
Use `/close-session [topic]`. Updates memory, prunes stale lessons, archives handoff, and commits.

## Quality Standards

This project enforces:

- **Ruff**: Linting and formatting (`ruff check --fix . && ruff format .`)
- **Mypy**: Static type checking (`mypy src/`)
- **Pytest**: Full test suite (87 tests, 100% passing)
- **Self-analysis**: `qgis-analyzer analyze .` for quality metrics
- **Conventional Commits**: Standard commit message format

## Runtime

This system runs natively under **opencode**. Subagents are registered in `opencode.json`; skills are discovered via `skills.paths`. No runtime bridge is required.

---

*Generation 8 — opencode-native. Adapted from the SecInterp Gen 7 → Gen 8 evolution (2026-09-14).*
