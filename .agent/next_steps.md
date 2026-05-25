# Next Steps — Phase: Gen 6 Agentic System Upgrade (Updated 2026-05-25)

## Current Phase: Agentic System Gen 5 → 6

Comparative audit vs sec_interp (Gen 6→7) revealed gaps in observability, memory lifecycle, and runtime adaptation. This phase closes those gaps.

### Goal 1: Complete Gen 6 Foundation
- [ ] Create `scripts/sync_metrics.py` — auto-analysis with qgis-analyzer <!-- id: 1.1 -->
- [ ] Expand `QUICK_REFERENCE.md` to full skill/workflow reference (≥ 80 lines) <!-- id: 1.2 -->
- [ ] Add `i18n-standards` to AGENTS.md skills matrix <!-- id: 1.3 -->
- [ ] Add `audit-plugin` to AGENTS.md workflow table <!-- id: 1.4 -->
- [ ] Run `/audit-plugin` self-analysis and record baseline metrics <!-- id: 1.5 -->

### Goal 2: Observability Pipeline
- [ ] Integrate `sync_metrics.py` into `/start-session` and `/close-session` <!-- id: 2.1 -->
- [ ] Create `scripts/check_cc.py` — cyclomatic complexity gate (port from sec_interp) <!-- id: 2.2 -->
- [ ] Add CC gate to `/create-commit` workflow <!-- id: 2.3 -->

### Goal 3: Documentation Quality
- [ ] Update `pyproject.toml` version for next release <!-- id: 3.1 -->
- [ ] Review and update `AI_CONTEXT.md` with current metrics <!-- id: 3.2 -->
- [ ] Generate fresh self-analysis report <!-- id: 3.3 -->

## Completed
- [x] I18n wrapper recognition (`QCoreApplication.translate()`) — commit ddf12b7
- [x] 11 i18n wrapper test cases
- [x] `.agent/README.md` — system overview
- [x] `workflows/index.md` — CodeWhale runtime bridge
- [x] `architecture/IMPROVEMENT_PLAN.md` — Gen 5→6 roadmap
- [x] `memory/memory_policy.md` — 3-tier memory lifecycle
- [x] `memory/agent_metrics.json` — structured metric tracking
- [x] `AGENT_LESSONS.md` — restructured to YAML format
- [x] `workflows/audit-plugin.md` — self-audit workflow
- [x] `skills/i18n-standards/SKILL.md` — i18n standards for the analyzer
- [x] `task.md` and `next_steps.md` reactivated with active phase

## How to Resume
1. Run `/start-session` to sync context and metrics
2. Check `task.md` for active items
3. Continue with Goal 1.1: create `scripts/sync_metrics.py`
