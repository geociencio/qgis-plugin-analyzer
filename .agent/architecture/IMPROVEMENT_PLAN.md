# Agentic System Improvement Plan — qgis-plugin-analyzer

> **Created**: 2026-05-25 | **Based on**: Comparative audit vs sec_interp Gen 6→7 system
> **Scope**: .agent/ system integrity, observability, and runtime adaptation
> **Target**: Generation 6

---

## Executive Summary

The qgis-plugin-analyzer `.agent/` system is at **Generation 5** maturity. It has a functional skill/workflow architecture with 10 skills and 10 workflows, but lacks observability, memory lifecycle management, and a runtime bridge. The sec_interp system (Gen 6→7) provides a clear upgrade path.

### Gen 5 Baseline

| Component | Status |
|-----------|--------|
| AGENTS.md | ✅ Complete — 3 roles, skill matrix |
| Skills | ✅ 10 skills (coding, commit, docs, domain, QA, release, etc.) |
| Workflows | ✅ 10 workflows (start/close-session, create-commit, run-tests, etc.) |
| QUICK_REFERENCE.md | ⚠️ Skeletal — 21 lines |
| task.md / next_steps.md | ❌ Stale — marked "Completed", no active phase |
| architecture/ | ❌ Missing |
| memory/agent_metrics.json | ❌ Missing |
| memory/memory_policy.md | ❌ Missing |
| workflows/index.md | ❌ Missing |
| scripts/sync_metrics.py | ❌ Missing |
| .agent/README.md | ❌ Missing |
| i18n-standards skill | ❌ Missing |

---

## Phase 0: Gen 5 → 6 Foundation ✅ IN PROGRESS

**Executed**: 2026-05-25

### 0.1 Create Missing Infrastructure
- [x] `.agent/README.md` — system overview
- [x] `workflows/index.md` — CodeWhale runtime bridge
- [x] `architecture/IMPROVEMENT_PLAN.md` — this file
- [ ] `memory/memory_policy.md` — memory lifecycle
- [ ] `memory/agent_metrics.json` — structured metrics
- [ ] `scripts/sync_metrics.py` — auto-analysis script

### 0.2 Reactivate Active Documents
- [ ] `task.md` — new active phase with IDs
- [ ] `next_steps.md` — active goals with IDs

### 0.3 Expand Critical Files
- [ ] `QUICK_REFERENCE.md` — expand to full skill/workflow reference
- [ ] `AGENT_LESSONS.md` — restructure to YAML format

### 0.4 Add Missing Skills & Workflows
- [ ] `workflows/audit-plugin.md` — self-audit workflow
- [ ] `skills/i18n-standards/SKILL.md` — i18n standards for the analyzer

---

## Phase 1: Observability

### 1.1 Metric Sync Automation
Create `scripts/sync_metrics.py` that:
1. Runs `qgis-analyzer analyze .`
2. Extracts scores from `analysis_results/project_context.json`
3. Runs `python -m pytest tests/ -q` for test count
4. Writes to `agent_metrics.json`

### 1.2 Memory Lifecycle
- Define 3-tier model in `memory_policy.md`
- Episodic: session logs in `docs/maintenance/`
- Semantic: `AGENT_LESSONS.md` with YAML + `[consolidated]` tags
- Long-term: manual prune cycle

---

## Phase 2: Quality Elevation

### 2.1 Pre-commit Hooks
- Ruff + mypy validation
- Test pass requirement
- CC gate (optional, via `check_cc.py`)

### 2.2 Self-Audit Pipeline
- Integrate `/audit-plugin` into `/close-session`
- Compare metrics against baseline
- Block close if scores degrade

---

## Phase 3: Gen 7 Features (Future)

### 3.1 Context Selector
- Semantic skill injection based on task type
- Port `context_selector.py` from sec_interp

### 3.2 Metrics Dashboard
- Generate Markdown trend report
- Port `metrics_report.py` from sec_interp

### 3.3 Memory Pruning
- Auto-prune lessons older than 90 days
- Port `memory_prune.py` from sec_interp

---

## Completion Criteria (Gen 6)

- [ ] All Phase 0 items complete
- [ ] `sync_metrics.py` operational
- [ ] `agent_metrics.json` tracking 3+ sessions
- [ ] `memory_policy.md` defines lifecycle
- [ ] `QUICK_REFERENCE.md` ≥ 80 lines
- [ ] `/start-session` and `/close-session` fully functional in CodeWhale
- [ ] Self-audit shows no regressions

---
*Target: Gen 6 operational by end of session 2026-05-25*
