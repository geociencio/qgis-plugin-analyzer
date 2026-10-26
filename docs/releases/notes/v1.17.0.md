# v1.17.0: Portal Gate Integration 🛡️🐍

Minor release. The analyzer now owns the source-level half of the official-repository
gate: Flake8, real Bandit/detect-secrets adapters, a machine-readable security report,
`metadata.txt` rules and a one-flag `portal` profile. The 25 MB limit is no longer
applied to the source tree; qgis-manage enforces it on the built ZIP.

## Added

- **Flake8 adapter** (`analyzer/flake8_audit.py`, modeled on `ruff_audit.py`):
  `analyze --flake8` and `--linters ruff,flake8`. Uses the optional `flake8-json`
  formatter and falls back to parsing the default `path:row:col: CODE text` output.
  Findings are normalized to `FLAKE8_<code>` and exposed as `flake8_findings` /
  `flake8_metadata`.
- **Real security tools**: `security --tools native|bandit|detect-secrets|flake8`
  runs the actual tools, normalizes findings (`tool`, `rule_id`, `portal_severity`,
  `blocking`) and merges them with the native AST/secret findings. Missing tools are
  explicit via `tool_unavailable` and exit code `2`.
- **`security --json`**: versioned report with `findings`, `summary`, `tool_status`,
  `tool_unavailable` and `exit_code`; `--fail-on critical|warning|info|none`
  controls the gate.
- **Portal profile**: `[tool.qgis-analyzer.profiles.portal]` wires `linters`,
  `security_tools`, `security_fail_on`, `metadata_rules` and `fail_on`. Precedence is
  CLI > profile > default.
- **Five `METADATA_*` rules**: `METADATA_REPOSITORY`, `METADATA_VERSION`,
  `METADATA_QGIS4`, `METADATA_SUPPORTS_QT6` and `METADATA_CATEGORY`, evaluated in the
  `metadata` scope and exposed through `qgis_compliance.best_practices`.
- Optional extras: `qgis-analyzer[flake8]`, `[security]` and `[portal]`.

## Changed

- `security` now runs the **security scope** (previously the full `all` scope) and
  `--deep` really controls the native entropy heuristic. Focused scans default to
  regex-only secrets; `--deep` or a profile enables entropy.
- Native `high` findings map to `critical`/blocking, so a high-severity finding fails
  the default `security` gate.
- `analyze --profile portal` applies the `fail_on` security threshold and includes the
  metadata rules.
- The source-tree size check is **informational** (25 MB reference). The portal limit
  belongs to the built ZIP and is enforced by qgis-manage; the QGIS score no longer
  penalizes the source-tree size. `repository_compliance` gains
  `constraint_warnings`.
- `analyze --json` / `security --json` keep logs and progress on stderr, so stdout is
  machine-readable.
- JSON envelopes expose an additive `schema: 1` alias next to `schema_version`.
- `RULES.md` now lists **56** rules, including the new QGIS Metadata section.

## Fixed

- The Flake8 adapter now detects the `flake8_json_reporter` module shipped by
  `flake8-json`; previously it always fell back to the default output even when the
  extra was installed.
- `detect-secrets` now runs with the target project as its working directory and scans
  `.`; passing an absolute path previously produced an empty result set.
- `security` used to ignore its own scope and `--deep`; both are now honored.
- `analyze --json` no longer leaks the project-type log to stdout.

## Cross-repository contract

- JSON `schema` / `schema_version` remain **1**; new fields are additive.
- `security --json` findings use the portal severity enum (`critical`, `warning`,
  `info`) and expose `blocking`.
- Exit codes: `0` clean, `1` findings, `2` invalid input/tool unavailable.
- `tool_unavailable` is explicit; a missing tool is never converted into zero findings.
- No Python imports between qgis-manage and qgis-analyzer: qgis-manage invokes the
  analyzer CLI.
- `project_context.json` keeps the native `high`/`medium`/`low` severity vocabulary for
  backward compatibility; use `security --json` for the portal severity contract.

## Upgrade

```bash
pip install --upgrade qgis-plugin-analyzer

# Optional: real portal tools
pip install "qgis-plugin-analyzer[portal]"
```

Typical commands:

```bash
qgis-analyzer analyze . --flake8
qgis-analyzer analyze . --profile portal
qgis-analyzer security . --deep --tools bandit,detect-secrets,flake8 --json
```

## Quality

- **273 tests**, 89% coverage; `ruff check` + `mypy src/` clean.
- Self-analysis `--max-cc 15` green with 10 LOW findings.
- Rule catalog: **56** rules; Module Stability 54.1 · Maintainability 99.9 ·
  Security 100.0.
