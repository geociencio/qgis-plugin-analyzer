# Quick Reference: Workflows + Skills System

**Created**: 2026-02-14 | **Updated**: 2026-05-25 (Gen 5 → 6)
**Version**: 2.0

---

## Executive Summary

The qgis-plugin-analyzer project features a system of **11 skills** and **11 workflows** integrated to automate AI-assisted development. As of 2026-05-25, the system is transitioning from Generation 5 to Generation 6 with the addition of observability, memory lifecycle, and a CodeWhale runtime bridge.

---

## Available Skills (11)

| Skill | Description | When to Use |
|:------|:------------|:------------|
| [agentic-memory](file://./skills/agentic-memory/SKILL.md) | Lessons and patterns management | Extracting meta-lessons, preferences |
| [changelog-generator](file://./skills/changelog-generator/SKILL.md) | Automated changelog from git commits | Writing release notes, CHANGELOG updates |
| [coding-standards](file://./skills/coding-standards/SKILL.md) | Project coding standards | Writing Python code, refactoring |
| [commit-standards](file://./skills/commit-standards/SKILL.md) | Conventional Commits standards | Creating commits, validating messages |
| [documentation-standards](file://./skills/documentation-standards/SKILL.md) | Logs and project history standards | Updating development/maintenance logs |
| [domain-logic](file://./skills/domain-logic/SKILL.md) | Business logic and data validation | Implementing new rules, core processing |
| [i18n-standards](file://./skills/i18n-standards/SKILL.md) | i18n standards for the analyzer | Modifying i18n visitor, translation audits |
| [project-context](file://./skills/project-context/SKILL.md) | Project purpose and architecture | Starting tasks, requesting overviews |
| [qa-docker](file://./skills/qa-docker/SKILL.md) | Docker testing environments | Running integration tests |
| [qa-standards](file://./skills/qa-standards/SKILL.md) | Automated testing and CI/CD | Writing tests, designing strategies |
| [release-management](file://./skills/release-management/SKILL.md) | Python package release process | Preparing releases, versioning |

---

## Available Workflows (11)

### Daily Development

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:---------|
| [/start-session](file://./workflows/start-session.md) | Senior Architect | project-context, domain-logic | Start session with synced context |
| [/create-commit](file://./workflows/create-commit.md) | QA Engineer | commit-standards, qa-standards | Commit with quality validation |
| [/run-tests](file://./workflows/run-tests.md) | QA Engineer | qa-docker, qa-standards | Run tests with interpretation |
| [/close-session](file://./workflows/close-session.md) | QA Engineer | commit-standards, documentation-standards | Close session with memory update |

### Refactoring and Quality

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:---------|
| [/refactor-code](file://./workflows/refactor-code.md) | Senior Architect | coding-standards | Refactor code with validation |
| [/audit-plugin](file://./workflows/audit-plugin.md) | Agent Auditor | project-context, qa-standards | Full self-analysis with qgis-analyzer |
| [/fix-linting](file://./workflows/fix-linting.md) | QA Engineer | coding-standards | Automatically fix style issues |

### Features and Review

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:---------|
| [/build-feature](file://./workflows/build-feature.md) | Architect | domain-logic | Pipeline for new features |
| [/ia-critic](file://./workflows/ia-critic.md) | Agent Auditor | agentic-memory | Plan review and validation |

### Release and Standards

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:---------|
| [/release-package](file://./workflows/release-package.md) | QA & Release | release-management, qa-docker | Release to PyPI |
| [/verify-standards](file://./workflows/verify-standards.md) | Senior Architect | documentation-standards | Audit agent system integrity |

---

## Quality Gate Scripts

| Script | Command |
|--------|---------|
| Full analysis | `uv run qgis-analyzer analyze .` |
| Metric sync | `uv run python scripts/sync_metrics.py` |
| Skill sync | `uv run python scripts/skill_sync.py` |
| Lint check | `uv run ruff check .` |
| Lint fix | `uv run ruff check --fix . && uv run ruff format .` |
| Type check | `uv run mypy src/` |
| Test suite | `python -m pytest tests/ -v` |
| Build check | `uv run python -m build && twine check dist/*` |
| AI context | `uv run ai-ctx analyze --path .` |

---

## Quick Reference Card

```
Start session:            /start-session
Close session:            /close-session [topic]
Quality commit:           /create-commit [message]
Run tests:                /run-tests

Safe refactor:            /refactor-code [file]
Self-audit:               /audit-plugin
Auto-linting:             /fix-linting

New feature:              /build-feature [desc]
Plan review:              /ia-critic

Release:                  /release-package
Verify standards:         /verify-standards
```

## Runtime

This system runs on **CodeWhale / DeepSeek V4**. The `workflows/index.md` file maps each workflow to concrete shell commands for the CodeWhale runtime. See `.codewhale/instructions.md` for the runtime bridge configuration.
