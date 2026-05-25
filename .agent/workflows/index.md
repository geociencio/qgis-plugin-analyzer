# Workflow Index — CodeWhale Runtime

> Maps each `.agent/workflows/*.md` to concrete CodeWhale actions.
> For humans: "I want to run X, what do I tell the agent?"
> For agents: "User said /X, what do I actually do?"

---

## Daily Development

### `/start-session`
**Tell the agent**: "Run /start-session"
**What happens**:
```
uv run ai-ctx analyze --path .
cat .agent/next_steps.md
cat .agent/task.md
cat .agent/memory/AGENT_LESSONS.md
uv sync
```
**Expected output**: Updated context, active tasks visible, dependencies OK.

### `/close-session`
**Tell the agent**: "Run /close-session with topic [name]"
**What happens**:
```
# Run full test suite
python -m pytest tests/ -q

# Update AGENT_LESSONS.md with 3 lessons from session
# Update next_steps.md with handover
# Archive next_steps to .agent/history/next_steps/next_steps_YYYY-MM-DD.md
# Create docs/maintenance/session_YYYY-MM-DD_[topic].md
# Add entry to docs/DEVELOPMENT_LOG.md
# Update CHANGELOG.md [Unreleased] from git log

git add . && git commit -m "chore(docs): close session [topic]"
```

### `/create-commit`
**Tell the agent**: "Run /create-commit with message [msg]"
**What happens**:
```
uv run ruff check --fix .
uv run ruff format .
uv run mypy src/
git add [files] && git commit -m "[msg]"
```

### `/run-tests`
**Tell the agent**: "Run /run-tests"
**What happens**:
```
python -m pytest tests/ -v --tb=short
```

---

## Refactoring & Quality

### `/refactor-code`
**Tell the agent**: "Run /refactor-code on [file/module]"
**What happens**: Reads coding-standards skill → applies changes → validates tests → ruff check.

### `/audit-plugin`
**Tell the agent**: "Run /audit-plugin"
**What happens**: `uv run qgis-analyzer analyze .` → review `analysis_results/`

### `/fix-linting`
**Tell the agent**: "Run /fix-linting"
**What happens**: `uv run ruff check --fix . && uv run ruff format .`

---

## Features & Review

### `/build-feature`
**Tell the agent**: "Run /build-feature [description]"
**What happens**: Reads domain-logic skill → implements → /ia-critic review → /create-commit

### `/ia-critic`
**Tell the agent**: "Run /ia-critic on [plan]"
**What happens**: Reads AGENT_LESSONS.md → cross-references AGENTS.md → issues verdict

---

## Release & Planning

### `/release-package`
**Tell the agent**: "Run /release-package"
**What happens**: Reads release-management skill → `uv run qgis-analyzer analyze . --profile release --strict` → build → `twine check`.

### `/verify-standards`
**Tell the agent**: "Run /verify-standards"
**What happens**: Audits all SKILL.md files for YAML structure, English language, and required sections.

---

## Quality Gate Commands (Direct)

| Gate | Command |
|------|---------|
| Full analysis | `uv run qgis-analyzer analyze .` |
| Lint check | `uv run ruff check .` |
| Type check | `uv run mypy src/` |
| Test suite | `python -m pytest tests/ -v` |
| Build check | `uv run python -m build && twine check dist/*` |

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
