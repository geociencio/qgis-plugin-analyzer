# Next Steps — Handover (2026-10-11, v1.16.0 released)

## Session Summary (topics: `module_splits` · `incremental_cache` · `rule_registry` · `standards`)

Shipped **v1.16.0** (minor): an incremental per-file cache (`--no-cache`) and a
unified rule registry that drives `list-rules` (all 51 rules) and a generated
`RULES.md`, plus a standards reconciliation (per-rule severity from the catalog,
`MISSING_I18N` gated for generic projects, Forge metrics baseline, CLI/test
hygiene) and a self-analysis noise cleanup. Released on **GitHub + PyPI** via CI.

### Completed
- [x] Module splits — `engine`/`fixer`/`summary_reporter`/`commands` ≤ 400 lines.
- [x] Incremental cache + `--no-cache` (`module_cache.py`; deterministic, path-sorted output).
- [x] Unified rule registry (`src/analyzer/rules/`) + generated `RULES.md`; enumerable security/secret ids; anti-drift tests.
- [x] Standards — catalog severity, i18n gate for generic projects, Forge `summary` baseline, worktree hygiene; docstrings + type hints at 100%; magic numbers extracted; `NON_PYTHONIC_LOOP` narrowed.
- [x] **v1.16.0** released (GitHub release published; PyPI `1.16.0` wheel + sdist; `twine check` PASSED).
- [x] **Agentic framework**: `agentic-forge` bumped `v1.2.0 → v1.4.1` (tests/CI,
  `forge.py --version`, `forge.py project <cmd>`, strict validation); `forge.toml`
  now declares `test_command`, `test_command_full`, `lint_command`, `format_command`,
  `type_command` and `strict_agent_system = true`; `qa-docker` references migrated to
  `testing-standards` (deprecated alias kept upstream for v1.4.x).

## How to Resume
1. Run `/start-session`.
2. Nothing pending on the release — `1.16.0` is live on PyPI, and the GitHub
   release is published (Latest).

## Remaining / Next
- [x] ~~Module splits~~ · [x] ~~Fase 6 rule registry~~ · [x] ~~Fase 2.2 incremental cache~~ · [x] ~~Tune anti-pattern noise~~.
- [ ] **Optional**: decompose the two core classes to clear the last 10 LOW findings (`SPAGHETTI_CODE`, `GOD_OBJECT`) — higher risk.
- [ ] **Optional**: unify `CompositeVisitor._active_visitors` with `SCOPE_RULES` (currently a second scope→visitor map).

## 🐛 Known Issues

**None blocking** — 233 tests passing; `ruff check` + `mypy src/` clean; self-analysis `--max-cc 15` green (max func CC 13). Self-run issues down to 10 LOW (SPAGHETTI_CODE/GOD_OBJECT).

- **Metrics validator false positives — RESOLVED (agentic-forge v1.3.0)**:
  `forge.py metrics validate` used to flag **5** entries in the `.agent/` framework
  submodule — `scaffold/qgis/workflows/release-plugin.md` (CC ≤ 10 ×3, 763 tests →
  the SecInterp domain template) and `skills/coding-standards/SKILL.md`
  ("complexity below 10" → generic guideline). The v1.3.0 release excludes
  `scaffold/` from ground-truth checks and derives the CC guidance from
  `[project].max_cc`; the submodule was bumped from `v1.2.0` to `v1.3.0` and
  `forge.py metrics validate` now exits 0 (38 files scanned). Do **not** re-apply
  the old workaround or patch the submodule.

## Technical Debt
- [ ] Coverage: keep incremental gains (CI floor 80%).
- [ ] Optional core-class decomposition (see Remaining / Next).

## Watch-outs
- Keep the `project_context.json` schema keys stable (consumed by `ai-context-core`; bump `schema_version` on change).
- Keep CLI subcommands/flags stable (consumed by `qgis-plugin-manager`).
- Security rules: verify a registry populated by import side effects stays non-empty (see AGENT_LESSONS 2026-10-10).
- Cache: the signature covers analyzer version + source fingerprint + resolved project path + effective config; `--no-cache` is the escape hatch.
