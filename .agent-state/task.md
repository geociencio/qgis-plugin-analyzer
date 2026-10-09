# Active Tasks — Phase: Analyzer Generalization (COMPLETE — v1.14.0)

This task board tracks the current development phase based on `.agent/next_steps.md`.
Reference plan: `docs/plans/implementation_plan_generalize_analyzer.md`.

## Goal 1: Analyzer Generalization
- [x] Fase 0.1 — `schema_version` + `analyzer_version` in `project_context.json` <!-- id: 1.1 -->
- [x] Fase 0.2 — `--include-content` flag (content optional) <!-- id: 1.2 -->
- [x] Fase 0.3 — `--json` flag + clean stdout <!-- id: 1.3 -->
- [x] Fase 0.4 — legacy output dir warning <!-- id: 1.4 -->
- [x] Fase 1 — port i18n AST rule to `I18nVisitor` (replace heuristic) <!-- id: 1.5 -->
- [x] Fase 2 — CC gate `--max-cc N` <!-- id: 1.6 -->
- [x] Fase 3 — bump Python >=3.11 + remove `_minimal_toml_load` <!-- id: 1.7 -->
- [x] Fase 4 — tests (golden doc, synthetic, CC gate, back-compat) <!-- id: 1.8 -->
- [x] Fase 5 — docs reconciliation <!-- id: 1.9 -->

## Goal 2: Release Cleanup
- [x] Upload v1.14.0 to PyPI (manual — done by user) <!-- id: 2.1 -->
- [x] Fix setuptools license deprecation warnings <!-- id: 2.2 -->
- [x] ~~Add `i18n-standards` and `audit-plugin` triggers to `skill_sync.py`~~ (obsolete) <!-- id: 2.3 -->

## Goal 3: Technical Debt
- [ ] Reduce 297 self-reported MISSING_I18N in analyzer's own codebase <!-- id: 3.1 -->
- [ ] Address 3 HIGH_COMPLEXITY issues <!-- id: 3.2 -->

## Competitive Analysis Follow-ups
- [x] Req 1 — Qt6 migration rules (`QGS4xx` parity) via `QtTransitionVisitor` <!-- id: 4.1 -->
- [x] Req 2 — type-hint coverage counts all parameter kinds <!-- id: 4.2 -->
- [x] Req 4 (partial) — `summary` stale-cache detection <!-- id: 4.3 -->
- [ ] Req 3 — `ci-wizard` workflow generator <!-- id: 4.4 -->
- [ ] Req 5 — golden SecInterp validation (external corpus) <!-- id: 4.5 -->

## 🧠 Gen 8 Agentic System Evolution (COMPLETED 2026-09-14)
- [x] Phase A: root `AGENTS.md` SSoT; retired `skill_sync.py` + `init_agent_system.sh` <!-- id: 8.1 -->
- [x] Phase B: retired `.codewhale/` bridge; added `memory_prune.py` + `validate_agent_system.py` <!-- id: 8.2 -->
- [x] Phase D: native subagents in `opencode.json`; normalized workflow `agent:` ids <!-- id: 8.3 -->
- [ ] Phase E (follow-up): drop `trigger` from SKILL.md files <!-- id: 8.4 -->

## Completed
- [x] I18n fix: `QCoreApplication.translate()` wrapper recognition (v1.13.2)
- [x] Gen 5→6 agentic system upgrade (13 files, 895 insertions)
- [x] v1.13.2 GitHub release
- [x] Fase 0–5: analyzer generalization (i18n AST, `--max-cc`, Python 3.11, CI contract)
- [x] Qt6 migration rules (`QGS4xx` parity)
- [x] v1.14.0 release (GitHub + PyPI)

## Operational Status
- **Active Phase**: None (v1.14.0 released)
- **Current Metrics**:
  - Tests: 126/126 passing (100%)
  - Stability: 54.8/100
  - Maintainability: 88.1/100
  - Security: 100.0/100
