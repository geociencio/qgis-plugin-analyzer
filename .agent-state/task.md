# Active Tasks — Phase: Repo Hygiene & Hardening (COMPLETE — v1.15.0 prepared)

Reference plan: `docs/plans/implementation_plan_repo_hygiene_and_hardening.md`.

## Goal 1: Repo Hygiene & Hardening
- [x] Fase 0 — untrack generated artifacts, `.gitignore`, remove `migration/`, archive debug artifacts <!-- id: 1.1 -->
- [x] Fase 3a — CI ruff+mypy+pytest + `pythonpath` + N1 format fix <!-- id: 1.2 -->
- [x] Fase 1.2 — reliable ruff audit (`sys.executable -m ruff`, `tool_unavailable`) <!-- id: 1.3 -->
- [x] Fase 1.1 — transversal `# noqa` opt-out <!-- id: 1.4 -->
- [x] Fase 1.3 — path normalization <!-- id: 1.5 -->
- [x] Fase 2.1 — configurable workers + batching <!-- id: 1.6 -->
- [x] Fase 4 — refactor 3 functions below CC 15 <!-- id: 1.7 -->
- [x] Fase 3b — `--max-cc 15` self-gate + coverage floor <!-- id: 1.8 -->
- [x] Fase 5 — port patterns/anti-patterns/Halstead/optimizations <!-- id: 1.9 -->
- [x] Fase 6 — docs/DX (RULES.md + output contract + CI) <!-- id: 1.10 -->

## Goal 2: Release v1.15.0
- [x] Bump `pyproject.toml` + `uv.lock` to 1.15.0 <!-- id: 2.1 -->
- [x] CHANGELOG + `docs/releases/notes/v1.15.0.md` <!-- id: 2.2 -->
- [ ] Git tag + GitHub release (maintainer) <!-- id: 2.3 -->
- [ ] PyPI upload (manual, maintainer) <!-- id: 2.4 -->

## Deferred Follow-ups
- [ ] Fase 2.2 — incremental cache + `--no-cache` <!-- id: 3.1 -->
- [ ] Fase 4 — module decomposition + CLI layering + reporters base <!-- id: 3.2 -->
- [ ] Fase 6 — unified rule registry to auto-generate `RULES.md` <!-- id: 3.3 -->
