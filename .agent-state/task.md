# Active Tasks — Phase: Deep-Analysis Backlog & Security Restore (COMPLETE — v1.15.2)

Reference: `docs/reports/DEEP_ANALYSIS_v1.15.0_DEAD_CODE_DUPLICATION.md`

## Goal 1: Deep-Analysis Backlog
- [x] P0 — reconnect `security_rules` + regression test <!-- id: 1.1 -->
- [x] P1 — `SCOPE_RULES` SSoT; reuse `I18N_METHODS`; delete dead code <!-- id: 1.2 -->
- [x] P2 — reduce CC (`run`/`visit_For`/`visit_Constant`); drop unused validators <!-- id: 1.3 -->
- [x] P3 — raise coverage graph/serve/fixer/summary (75→86%); CI floor 80 <!-- id: 1.4 -->

## Goal 2: Releases
- [x] v1.15.1 — bump, CHANGELOG, release notes, README, tag, push, GitHub Release <!-- id: 2.1 -->
- [x] v1.15.2 — fix `B102`/`B307` attribute-call false positives + release docs/CI (maintainer) <!-- id: 2.2 -->
- [x] PyPI upload of the latest release — verified live on PyPI (1.15.2 wheel + sdist, 2026-10-11T01:27Z via CI `publish-pypi`) <!-- id: 2.3 -->

## Goal 3: Docs
- [x] README deep update; comparison → `docs/research/COMPARISON_VS_ALTERNATIVES.md` <!-- id: 3.1 -->

## Deferred Follow-ups
- [ ] Module splits (engine/fixer/summary_reporter > 400 lines) <!-- id: 4.1 -->
- [ ] Fase 6 — unified rule registry to auto-generate `RULES.md` <!-- id: 4.2 -->
- [ ] Fase 2.2 — incremental cache + `--no-cache` <!-- id: 4.3 -->

## Operational Status
- **Active Phase**: None — all goals complete; v1.15.2 released on **GitHub + PyPI**.
- **Current Metrics**: 194/194 tests; `ruff` + `mypy` clean; self-analysis `--max-cc 15` green (max func CC 13); Module Stability 53.9 · Maintainability 86.7 · Security 100.0.
- **Known**: 4 `forge.py metrics validate` false positives in `.agent/` framework scaffold/generic skills (see `next_steps.md` → Known Issues). Non-blocking; mirrors `ai-context-core`.
