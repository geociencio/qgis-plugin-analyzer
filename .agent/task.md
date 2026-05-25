# Active Tasks — Phase: Gen 6 Observability Pipeline

This task board tracks the current development phase based on `.agent/next_steps.md`.

## Goal 1: Observability Pipeline
- [ ] Port `check_cc.py` from sec_interp for CC gate <!-- id: 1.1 -->
- [ ] Create `scripts/metrics_report.py` for trend dashboard <!-- id: 1.2 -->
- [ ] Integrate `sync_metrics.py` into `/start-session` and `/close-session` <!-- id: 1.3 -->

## Goal 2: Release Cleanup
- [ ] Upload v1.13.2 to PyPI (manual) <!-- id: 2.1 -->
- [ ] Fix setuptools license deprecation warnings <!-- id: 2.2 -->
- [ ] Add `i18n-standards` and `audit-plugin` triggers to `skill_sync.py` <!-- id: 2.3 -->

## Goal 3: Technical Debt
- [ ] Reduce 570 self-reported MISSING_I18N in analyzer's own codebase <!-- id: 3.1 -->
- [ ] Address 2 HIGH_COMPLEXITY issues in `ast_utils.py` <!-- id: 3.2 -->

## Completed
- [x] I18n fix: `QCoreApplication.translate()` wrapper recognition (v1.13.2)
- [x] Gen 5→6 agentic system upgrade (13 files, 895 insertions)
- [x] v1.13.2 GitHub release

## Operational Status
- **Active Phase**: Gen 6 Observability Pipeline
- **Current Metrics**:
  - Tests: 87/87 passing (100%)
  - Stability: 55.2/100
  - Maintainability: 77.0/100
  - Security: 100.0/100
