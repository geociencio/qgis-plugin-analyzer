
# Walkthrough: AI Context Core Extraction

The extraction of AI context logic into a standalone package named `ai-context-core` has been completed.

## 📦 New Package
Location: `migration/ai-context-core/`

This folder is a **self-contained Python repository** ready to be moved to its own git repository.

### Structure
```
ai-context-core/
├── pyproject.toml       # Package definition and dependencies (click, rich, pyyaml)
├── README.md            # Usage instructions
├── src/
│   └── ai_context_core/
│       ├── cli.py       # Entry point (init, analyze commands)
│       ├── analyzer/    # Refactored analysis logic (engine, metrics, ast...)
│       ├── config/      # Profile system and configuration loader
│       ├── context/     # Context manager and prompt templates
│       └── templates/   # Workflows (.md) and Initial Prompt
```

## 🛠️ Implemented Tools

### CLI (`ai-ctx`)
Main command installed by the package via `project.scripts`.
- `ai-ctx init --profile qgis-plugin`: Initializes `.ai-context` in a project.
- `ai-ctx analyze`: Runs optimized analysis and updates the project brain.
- `ai-ctx profiles`: Lists available profiles.

### Profile System
A flexible configuration system was implemented in `src/ai_context_core/config/`.
- **Defaults**: Base configuration in `defaults.yaml`.
- **Profiles**: YAML files in `profiles/` (e.g., `qgis.yaml`) that override defaults.
- **Overrides**: Local configuration in `.ai-context/config.yaml` has the highest priority.

## 📚 Documentation
A organized `docs/` folder has been included:
- [`ARCHITECTURE.md`](../development/ARCHITECTURE.md): Technical design and data flow.
- [`CONTRIBUTING.md`](../development/CONTRIBUTING.md): Developer guide (setup with `uv`).
- [`PROFILES_GUIDE.md`](../user_guide/PROFILES_GUIDE.md): How to create and modify analysis profiles.
- [`CHANGELOG.md`](../../CHANGELOG.md): Change log (v0.1.0).

## 🔄 Logic Migration
The monolithic logic of `analyze_project_optfixed.py` was modularized:
- **`engine.py`**: Main orchestrator.
- **`ast_utils.py`**: Static code analysis (AST).
- **`metrics.py`**: KPI calculation and quality scores.
- **`dependencies.py`**: Import graph analysis.
- **`issues.py`**: Technical debt and security detection.
- **`fs_utils.py`**: Efficient file system handling (cache, mmap).
- **`reporting.py`**: Markdown generation for users and AI.

## 📝 Packaged Workflows
Agent workflows have been adapted to use the new `ai-ctx` CLI and are included in the package:
- `start-session.md`
- `end-session.md`
- `create-commit.md`

## ✅ Verification
The package is installable with modern tools like `uv` or `pip`:
```bash
cd migration/ai-context-core
uv sync
uv run ai-ctx --help
```
