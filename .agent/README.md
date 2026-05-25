# qgis-plugin-analyzer Agentic System (Generation 5 → 6)

Welcome to the **qgis-plugin-analyzer Agentic Intelligence Core**. This directory contains the brain, tools, and protocols for AI-assisted development of the QGIS Plugin Analyzer.

## Overview

Based on the **Gentleman Programming** system with a partitioned context model and modular skills. Currently transitioning from Generation 5 to Generation 6.

### Generation 6 Goals
1. **Observability**: Automated metric extraction via `sync_metrics.py`
2. **Memory Lifecycle**: 3-tier memory model with pruning
3. **Runtime Bridge**: `workflows/index.md` for CodeWhale adaptation
4. **Self-Audit**: Run the analyzer on its own codebase

## Directory Structure

```
.agent/
├── AGENTS.md               # Role definitions & skill mappings
├── QUICK_REFERENCE.md      # Fast lookup for skills and workflows
├── README.md               # This file — system overview
├── next_steps.md           # Active goals and handoff state
├── task.md                 # Active task board
├── init_agent_system.sh    # System initialization script
├── architecture/           # System design and improvement plans
│   └── IMPROVEMENT_PLAN.md # Gen 5→6 roadmap
├── memory/                 # Cognitive history and lessons
│   ├── AGENT_LESSONS.md    # Structured technical lessons
│   ├── agent_metrics.json  # Operational metrics
│   └── memory_policy.md    # Memory lifecycle policy
├── skills/                 # On-demand capabilities (11)
│   ├── domain-logic/       # Business logic and validation
│   ├── i18n-standards/     # i18n standards for the analyzer itself
│   └── ... (see QUICK_REFERENCE.md)
├── workflows/              # Standardized procedures (11)
│   ├── index.md            # CodeWhale runtime quick reference
│   ├── start-session.md    # Initializing with context
│   ├── close-session.md    # Closing with memory update
│   └── ... (see QUICK_REFERENCE.md)
├── scripts/                # Agent system utilities
│   └── skill_sync.py       # Regenerate dynamic triggers in AGENTS.md
└── history/                # Archived task boards and next_steps snapshots
    ├── tasks/              # Phase task archives
    └── next_steps/         # Session handoff snapshots
```

## How to Use

### Starting a Session
Always start with `/start-session`. This syncs context, reads active tasks, and validates the environment.

### Developing and Testing
Use specialized workflows like `/build-feature` or `/refactor-code`. The `/ia-critic` workflow reviews plans before implementation.

### Committing
Use `/create-commit`. Validates linting, types, and commit message format.

### Closing a Session
Use `/close-session [topic]`. Updates memory, creates session log, and prepares handoff for the next session.

## Quality Standards

This project enforces:
- **Ruff**: Linting and formatting (`ruff check --fix . && ruff format .`)
- **Mypy**: Static type checking (`mypy src/`)
- **Pytest**: Full test suite (87 tests, 100% passing)
- **Self-analysis**: `qgis-analyzer analyze .` for quality metrics
- **Conventional Commits**: Standard commit message format

## Runtime Adaptation
This system was designed for Antigravity/Gemini but is fully operational in CodeWhale/DeepSeek V4. See `workflows/index.md` for the runtime bridge.

---
*Antigravity Framework — Generation 5 → 6*
