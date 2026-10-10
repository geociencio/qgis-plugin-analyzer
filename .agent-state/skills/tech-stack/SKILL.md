---
name: tech-stack
description: Toolchain, dependency management with uv, and quality tools for qgis-plugin-analyzer.
trigger: when installing dependencies, configuring the environment, or running linting/type-checking/formatting.
---

# Tech Stack

Defines the ecosystem of tools and libraries that sustain `qgis-plugin-analyzer` development.

## When to use this skill
- When installing new dependencies.
- When configuring the development environment.
- When running linting, formatting, or type checking.
- When verifying Python version compatibility.

## Degree of Freedom
- **Strict**: `uv` as package manager is mandatory.

## Workflow
1. **Manage**: Use `uv` for any package operation.
2. **Synchronize**: Keep the environment up to date with `uv sync`.
3. **Quality**: Run `ruff` for static validation and `mypy` for typing.

## Instructions and Rules

### 1. Core Technologies
- **Python**: >= 3.11
- **Manager**: `uv` (replaces pip/poetry)
- **Quality**: `ruff` (configured in `pyproject.toml`; single linter/formatter) + `mypy` (static types)
- **Tests**: `pytest`

### 2. Dependency Management
- **Add**: `uv add [package]`
- **Dev**: `uv add --dev [package]`
- **Install**: `uv sync`

### 3. Code Quality
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Types**: `uv run mypy src/`
- **Tests**: `uv run python -m pytest tests/ -q`
- **Self-analysis**: `uv run qgis-analyzer analyze . --max-cc 15`

## Quality Checklist
- [ ] Is `uv` prioritized?
- [ ] Are the exact `ruff`, `mypy`, and `pytest` commands mentioned?
- [ ] Is the Python version correct (`>= 3.11`)?
- [ ] Are obsolete tools (pip/venv) avoided?
