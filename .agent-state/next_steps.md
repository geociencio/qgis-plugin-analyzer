# Next Steps — Handover (2026-10-19, agentic-forge v1.4.2)

## Session Summary (topics: `repository_audit` · `agentic_forge` · `framework_upgrade` · `docs`)

Audited this repository and the shared `agentic-forge` framework, produced the
repository/analysis reports under `docs/reports/`, and upgraded the framework
`v1.2.0 → v1.3.0 → v1.4.1 → v1.4.2` with the new `forge.py project` command contract
and strict validation. No analyzer source code changed; all project gates are green.

### Completed
- [x] Repository audit — `docs/reports/DEEP_ANALYSIS_v1.16.0_REPOSITORY_AUDIT.md`.
- [x] Framework baseline + deltas — `docs/reports/DEEP_ANALYSIS_AGENTIC_FORGE_v1.2.0.md`,
  `AGENTIC_FORGE_v1.3.0_UPDATE.md`, `AGENTIC_FORGE_v1.4.1_UPDATE.md`,
  `AGENTIC_FORGE_v1.4.2_UPDATE.md`.
- [x] `agentic-forge` bumps: `v1.3.0` (`b41facd`), `v1.4.1` (`a98f5a8`),
  `v1.4.2` (`b98186a`); current submodule `537f9fd` → `b264e35` (recorded `v1.4.2`).
- [x] `forge.toml` now declares `test_command`, `test_command_full`, `lint_command`,
  `format_command`, `type_command` and `strict_agent_system = true`.
- [x] `AGENTS.md`: `/i18n-maintenance` added; `qa-docker` removed from the active skill
  list and documented as a deprecated alias for `testing-standards`.
- [x] Upstream framework v1.3.0+ fixed the 5 `metrics validate` false positives; the
  former "Known Issue" is resolved.
- [x] **v1.16.0** remains the released analyzer version (GitHub + PyPI).
- [x] **Analyzer P0 + P1 upstream gate integration** (2026-10-25): Flake8 adapter +
  `analyze --flake8/--linters`; real Bandit/detect-secrets/Flake8 adapters behind
  `security --tools --json --fail-on`; security scope/`--deep` fix; 25 MB source-tree
  rule moved to informational; portal profile with CLI > profile > default precedence;
  five `METADATA_*` catalog rules. qgis-manage's artifact layer is implemented in the
  sibling repository (v0.13.0+).

## How to Resume
1. Run `/start-session`.
2. Nothing pending on the analyzer release — `1.16.0` is live on PyPI and GitHub.
3. The framework is on `v1.4.2`; the five reports under `docs/reports/` are committed as
   part of this close-session (previously untracked).

## Remaining / Next
- [x] ~~Module splits~~ · [x] ~~Fase 6 rule registry~~ · [x] ~~Fase 2.2 incremental cache~~ · [x] ~~Tune anti-pattern noise~~.
- [ ] **Optional**: decompose the two core classes to clear the last 10 LOW findings (`SPAGHETTI_CODE`, `GOD_OBJECT`) — higher risk.
- [ ] **Optional**: unify `CompositeVisitor._active_visitors` with `SCOPE_RULES` (currently a second scope→visitor map).
- [ ] **P2**: JSON schema snapshots, real-tool CI job with the `[portal]` extras, and
  `flake8_config` wiring (see `docs/research/upstream_gate_integration.md`).
- [ ] **Upstream framework follow-ups** (not blocking this repo):
  - make the framework test suite self-contained (2 consumer-coupled tests keep its CI red
    when run in a standalone checkout);
  - fix `forge.py metrics report` on `task_completion_rate: None`
    (`forge_metrics_report.py:193`); project data is normalized to `1.0` meanwhile;
  - complete the structural checklist (5/9 skills, 7/14 workflows);
  - resolve the `pre-commit` wording and document `version_bump_command`.

## 🐛 Known Issues

**None blocking** — 273 tests passing; `ruff check` + `mypy src/` clean; self-analysis
`--max-cc 15` green (max func CC 13); self-run issues are 10 LOW
(`SPAGHETTI_CODE` 8, `GOD_OBJECT` 2).

- **Metrics validator false positives — RESOLVED (agentic-forge v1.3.0+)**:
  `forge.py metrics validate` used to flag 5 entries in the scaffold/generic skills.
  v1.3.0 excludes `scaffold/` from ground-truth checks and derives the CC guidance from
  `[project].max_cc`; with v1.4.2 the command exits 0 (38 files). Do **not** re-apply the
  old workaround or patch the submodule.
- **Upstream-only**: the framework's standalone CI is still red on 2 consumer-coupled
  tests and the structural checklist is partial; track upstream, do not patch the
  submodule.

## Technical Debt
- [ ] Coverage: keep incremental gains (CI floor 80%).
- [ ] Optional core-class decomposition (see Remaining / Next).

## Watch-outs
- Keep the `project_context.json` schema keys stable (consumed by `ai-context-core`; bump `schema_version` on change).
- Keep CLI subcommands/flags stable (consumed by `qgis-plugin-manager`).
- Security rules: verify a registry populated by import side effects stays non-empty (see AGENT_LESSONS 2026-10-10).
- Cache: the signature covers analyzer version + source fingerprint + resolved project path + effective config; `--no-cache` is the escape hatch.
- Framework: `forge.py project` commands are read from `forge.toml`; keep the five command
  keys in sync with the project runners when the toolchain changes.
