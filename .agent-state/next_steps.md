# Next Steps — Handover (2026-11-02, v1.19.2)

## Session 2026-11-02 — `session_init_validation` (no code changes)

`/start-session` revalidated the post-v1.19.2 state: submodule synced, `ruff`
clean, 313/313 tests (89.49% coverage), self-analysis 10 LOW (max CC 13), 37
framework tests. `scripts/sync_metrics.py` refreshed the 2026-11-02 entry and
this close rotated `last_session` (the old block still pointed at 2026-10-26/283
tests). Only `.agent-state/` bookkeeping changed; release line unchanged.

## Session Summary (topics: `portal_gate` · `ignore_aware_analysis` · `distribution_boundary` · `signal_connections` · `release_v1.19.2`)

Completed the portal-gate integration, fixed the real Bandit/detect-secrets/Flake8
adapters, shipped the `security --json` contract, and released two minor versions:
**v1.17.0** (portal gate) and **v1.18.0** (ignore-aware analysis).

### Completed
- [x] **v1.17.0** — Flake8 adapter, real security tools, `security --json`, portal
  profile, five `METADATA_*` rules, 25 MB source-tree informational rule; GitHub + PyPI.
- [x] **v1.18.0** — ordered `.gitignore`/`.qgisignore`/`.analyzerignore` matcher with
  `!` negation, `--exclude` on `analyze`/`security`/`fix`, `--scope` on `analyze`,
  default `docs/`/`tests/` exclusions; GitHub + PyPI.
- [x] **v1.18.1** — distribution boundary fix: wheel only `analyzer/*` + `.dist-info`,
  sdist only tool source + install metadata; **released on GitHub + PyPI** (CI `publish-pypi`).
- [x] **v1.19.0** — per-connection `SIGNAL_LEAK` resolver, `--signals`, opt-in `emit`, JSON contract; **released on GitHub + PyPI** (CI `publish-pypi`).
- [x] Issue #1 regression fixes; **released in v1.19.1** on GitHub + PyPI (CI `publish-pypi`).
- [x] Issue #1 follow-ups R4–R6 (+R3 addWidget hints); **released in v1.19.2** on GitHub + PyPI.
- [x] Real-tool fixes: `flake8_json_reporter` detection and detect-secrets project cwd;
  verified against the installed `[portal]` extras.
- [x] README, `COMMANDS_GUIDE.md`, CHANGELOG, release notes, `GITHUB_RELEASE_*`, and
  development log updated; `agent_metrics.json` synced (285 tests, 54.0/99.9/100).
- [x] Release pipeline verified: tag → draft release → published release → CI PyPI job.

## How to Resume
1. Run `/start-session`.
2. Nothing pending on the release — **v1.19.2** is live on PyPI and GitHub.
3. Read `docs/maintenance/session_2026-10-25_ignore_aware_analysis.md` for the full
   session record.

## Remaining / Next
- [ ] **P2**: JSON schema snapshots, a CI job with the real `[portal]` extras, and
  `flake8_config` wiring (see `docs/research/upstream_gate_integration.md`).
- [ ] **Optional**: decompose the two core classes to clear the last 10 LOW findings
  (`SPAGHETTI_CODE`, `GOD_OBJECT`) — higher risk.
- [ ] **Optional**: unify `CompositeVisitor._active_visitors` with `SCOPE_RULES`.
- [ ] **Upstream framework follow-ups** (not blocking this repo):
  - make the framework test suite self-contained (2 consumer-coupled tests keep its CI
    red in a standalone checkout);
  - fix `forge.py metrics report` on `task_completion_rate: None`;
  - complete the structural checklist (5/9 skills, 7/14 workflows);
  - resolve the `pre-commit` wording and document `version_bump_command`.

## 🐛 Known Issues

**None blocking** — 313 tests passing; `ruff check` + `mypy src/` clean; self-analysis
`--max-cc 15` green (max func CC 13); self-run issues are 10 LOW
(`SPAGHETTI_CODE` 8, `GOD_OBJECT` 2).

## Technical Debt
- [ ] Coverage: keep incremental gains (CI floor 80%; currently 89.33%).
- [ ] Optional core-class decomposition (see Remaining / Next).

## Watch-outs
- **Ignore precedence**: defaults → `.gitignore` → `.qgisignore` → `.analyzerignore` →
  profile/CLI; last match wins. Use `--exclude '!docs/'` to restore a default exclusion.
- **External tools still scan the tree**: Bandit/detect-secrets/Flake8 run over the
  project, but their findings are filtered through the matcher before reporting.
- **JSON contract**: `schema`/`schema_version` stay `1`; new fields are additive.
  `security --json` uses `portal_severity` (`critical`/`warning`/`info`); the native
  `project_context.json` keeps `high`/`medium`/`low` for backward compatibility.
- **Cache**: the signature covers analyzer version + source fingerprint + resolved
  project path + effective config; `--no-cache` is the escape hatch.
- **Release pipeline**: `.github/workflows/release.yml` creates a draft on tag push and
  publishes to PyPI when the release is published. Push tags over HTTPS if SSH config
  permissions block `git@github.com`.
