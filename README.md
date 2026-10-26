# QGIS Plugin Analyzer 🛡️

👉 **[View Full Rules Catalog (RULES.md)](RULES.md)**

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/geociencio/qgis-plugin-analyzer?color=blue&logo=github&style=flat-square)](https://github.com/geociencio/qgis-plugin-analyzer/releases)
[![PyPI version](https://img.shields.io/pypi/v/qgis-plugin-analyzer?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/qgis-plugin-analyzer/)
[![PyPI downloads](https://img.shields.io/pypi/dm/qgis-plugin-analyzer?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/qgis-plugin-analyzer/)
[![Python Version](https://img.shields.io/pypi/pyversions/qgis-plugin-analyzer?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/geociencio/qgis-plugin-analyzer?style=flat-square&logo=github)](https://github.com/geociencio/qgis-plugin-analyzer/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/geociencio/qgis-plugin-analyzer?style=flat-square&logo=github)](https://github.com/geociencio/qgis-plugin-analyzer/network/members)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=flat-square)](https://github.com/geociencio/qgis-plugin-analyzer/graphs/commit-activity)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?logo=git&style=flat-square)](https://conventionalcommits.org)
[![CI](https://github.com/geociencio/qgis-plugin-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/geociencio/qgis-plugin-analyzer/actions/workflows/ci.yml)

**Quality Metrics:**

![Module Stability](https://img.shields.io/badge/Module%20Stability-54.0%2F100-yellow?style=flat-square)
![Maintainability](https://img.shields.io/badge/Maintainability-99.9%2F100-brightgreen?style=flat-square)
![Security Score](https://img.shields.io/badge/Security--Bandit-100.0%2F100-brightgreen?style=flat-square)
![Type Coverage](https://img.shields.io/badge/Type%20Hints-100.0%25-brightgreen?style=flat-square)
![Docstring Coverage](https://img.shields.io/badge/Docstrings-100.0%25-brightgreen?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-283%2F283%20passing-brightgreen?style=flat-square&logo=pytest)

The **QGIS Plugin Analyzer** is a static analysis tool designed specifically for QGIS (PyQGIS) plugin developers. Its goal is to elevate plugin quality by ensuring they follow community best practices and are optimized for AI-assisted development.

## ✨ Main Features

**Security & correctness**

- **Bandit-inspired Security Core**: Detects `eval`/`exec` (B307/B102), unsafe `pickle` (B301), `shell=True` (B602), SQL injection (B608) and hardcoded secrets; findings carry CWE ids.
- **External security tools (optional)**: `security --tools bandit,detect-secrets,flake8` runs the real portal tools, normalizes their findings (`portal_severity`, `blocking`) and emits `--json`; missing tools are reported as `tool_unavailable` with exit code `2`.
- **Deep Entropy Secret Scanner**: Detect hardcoded API keys, passwords and tokens via regex + information entropy (`security --deep`).
- **Extended Safety Audit**: Signal leaks, missing slots and UI-blocking loops, with `QgsTask` suggestions.
- **Qt Resource Validation**: Detects missing/broken resource paths (`:/plugins/...`).

**QGIS standards & modernization**

- **Precise AST rules**: i18n (`self.tr()` / `QCoreApplication.translate()`), obsolete API, protected members, mandatory cleanup, `iface`-as-argument, and more.
- **Qt6 Migration Rules**: 11 AST-based `QT6_*` rules (drop-in parity with `flake8-qgis` `QGS4xx`) detecting APIs removed in Qt6.
- **QGIS Metadata Rules**: 5 catalog-backed `METADATA_*` checks (repository, version, QGIS 4 readiness, deprecated `supportsQt6`, category) in the `metadata` scope and portal profile.
- **Official Repository Compliance**: Validates binaries and metadata URLs before upload. The source-tree size is informational; the portal 25 MB limit applies to the built ZIP (qgis-manage's artifact layer).

**Quality & maintainability**

- **Cyclomatic Complexity Gate**: `--max-cc N` fails CI when a function exceeds the threshold (`cc_gate`/`cc_violations` in `--json`).
- **Design Patterns & Anti-patterns**: Detects `singleton`/`factory`/`observer`/`strategy`/`decorator`, plus `GOD_OBJECT`, `SPAGHETTI_CODE`, `MAGIC_NUMBER`, `DEAD_CODE`.
- **Halstead Metrics & Optimizations**: Per-module Halstead metrics and `module_too_large` / `complexity_refactoring` suggestions.
- **Transversal `# noqa`**: Suppress any rule inline with `# noqa` (whole line) or `# noqa: RULE_ID` (single rule).
- **Enhanced Configuration Profiles**: Rule-level severity control (`error`, `warning`, `info`, `ignore`) via `pyproject.toml`.
- **Integrated Ruff Analysis**: Runs Ruff through the active interpreter, exposing `ruff_metadata.tool_unavailable` when unavailable.

**Architecture & performance**

- **High-Performance Engine**: `ProcessPoolExecutor` with single-pass AST traversal, shared worker context, a configurable worker count (`--workers`) and file batching.
- **Deep Semantic Analysis**: Cross-file dependency graph (Mermaid), circular-import detection and coupling metrics.
- **Project Auto-Detection**: Distinguishes official QGIS plugins from generic Python projects and tailors validation accordingly.
- **Advanced Ignore Engine**: respects `.gitignore`, `.qgisignore` and `.analyzerignore` (ordered, `!` negation), with default excludes for `docs/`, `tests/`, `.venv/` and `build/`; add extra patterns with `--exclude`.

**DX & integration**

- **Interactive Auto-Fix**: AST-based fixes (GDAL imports, PyQt bridge, logging, i18n) with Git-status verification and diff preview.
- **CI Output Contract**: `--json`, `--include-content`, and a versioned/schema'd `project_context.json` (`schema`/`schema_version`, `analyzer_version`, `ruff_metadata`, `patterns`, `optimizations`).
- **Quality Gates in CI**: `ruff` + `mypy` + `pytest` (coverage floor) and the `--max-cc` self-analysis gate on Python 3.11–3.13.
- **Embedded Web Server**: Built-in `serve` command to browse HTML reports.
- **Real-time Progress**: CLI progress bar with ETA tracking.
- **Integrated Lint Analysis**: Runs Ruff and, optionally, Flake8 (`--flake8` / `--linters ruff,flake8`) through the active interpreter, exposing `ruff_metadata` / `flake8_metadata` with explicit `tool_unavailable` flags.
- **Zero Runtime Dependencies**: Standard library only; Ruff is the only required external tool. Flake8, Bandit and detect-secrets are optional extras (`qgis-analyzer[flake8]`, `[security]`, `[portal]`).

## 🆕 What's New in v1.18.0

**Ignore-aware analysis** — the analyzer now respects your repository's ignore files
and focuses on plugin code by default.

- 🔍 **`.gitignore` / `.qgisignore` / `.analyzerignore`** — merged and evaluated in
  order; the last match wins and `!pattern` re-includes.
- 🚫 **Default excludes** — `docs/`, `tests/`, `.venv/` and `build/` are skipped, so
  the source-tree size reflects the plugin code.
- 🎛️ **`--exclude` / `--scope`** — repeatable excludes on `analyze`/`security`/`fix`,
  and an explicit scope flag while keeping `analyze [scope] [path]`.
- 🧹 **Consistent filtering** — Ruff, Flake8 and external security findings are
  filtered by the same matcher.

[**📖 Full Release Notes**](docs/releases/notes/v1.18.0.md) | [**🗺️ CLI Commands Roadmap**](docs/research/CLI_COMMANDS_ROADMAP.md)

## 🚀 Installation and Usage

### Installation with `uv` (Recommended):

If you have [uv](https://github.com/astral-sh/uv) installed, you can install the analyzer quickly and in isolation:

**1. As a global tool (isolated):**
```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-analyzer.git
```

**2. Standard pip installation (Git):**
```bash
pip install git+https://github.com/geociencio/qgis-plugin-analyzer.git
```

**3. Local installation for development:**
```bash
git clone https://github.com/geociencio/qgis-plugin-analyzer
cd qgis-plugin-analyzer
uv sync
```

### Installation with `pip`:
```bash
pip install .
```

### Main Commands:

**1. Analyze a Plugin (Full Analysis):**
```bash
qgis-analyzer analyze /path/to/your/plugin -o ./quality_report
```

**2. Specialized Analysis (NEW in v1.9.0):**
```bash
# Internationalization audit only
qgis-analyzer analyze i18n /path/to/your/plugin

# Security vulnerability scanning only
qgis-analyzer analyze security /path/to/your/plugin

# Performance and UI blocking detection only
qgis-analyzer analyze performance /path/to/your/plugin

# Dependency and coupling analysis only
qgis-analyzer analyze architecture /path/to/your/plugin

# QGIS metadata validation only
qgis-analyzer analyze metadata /path/to/your/plugin
```

**3. Auto-Fix issues (Dry Run):**
```bash
qgis-analyzer fix /path/to/your/plugin
```

**4. Legacy Support:**
The default command remains analysis if no subcommand is specified:
```bash
qgis-analyzer /path/to/your/plugin
```

## 🔄 Pre-commit Hook

You can run `qgis-plugin-analyzer` automatically before every commit to ensure quality. Add this to your `.pre-commit-config.yaml`:

```yaml
  - repo: https://github.com/geociencio/qgis-plugin-analyzer
    rev: main  # Use 'main' for latest features or a specific tag like v1.5.0
    hooks:
      - id: qgis-plugin-analyzer
```

## 🤖 GitHub Action

Use it directly in your CI/CD workflows:

```yaml
steps:
  - uses: actions/checkout@v4
  - name: Run QGIS Quality Check
    uses: geociencio/qgis-plugin-analyzer@main
    with:
      path: .
      output: quality_report
      args: --profile release
```

## ⚙️ Configuration (`pyproject.toml`)

You can customize the analyzer's behavior using a `[tool.qgis-analyzer]` section in your `pyproject.toml`.

```toml
[tool.qgis-analyzer]
# Profiles allow different settings for CI vs Local
[tool.qgis-analyzer.profiles.default]
strict = false
generate_html = false  # CLI default
exclude = ["generated/"]  # defaults already exclude docs/, tests/, .venv/, build/

[tool.qgis-analyzer.profiles.release]
strict = true
fail_on_error = true

# Portal/CI profile: real tools, metadata rules and a security gate.
[tool.qgis-analyzer.profiles.portal]
linters = ["ruff", "flake8"]
security_tools = ["native", "bandit", "detect-secrets", "flake8"]
security_fail_on = "critical"
metadata_rules = true
fail_on = "critical"

[tool.qgis-analyzer.profiles.default.rules]
GDAL_DIRECT_IMPORT = "error"    # Ban direct 'import gdal'
IFACE_AS_ARGUMENT = "warning"   # Warn on iface passed as an argument
MANUAL_RESOURCE_PATH = "ignore" # Ignore resource path checks

# i18n rule configuration (AST-based):
[tool.qgis-analyzer.profiles.default.rules.MISSING_I18N]
extra_ignore_calls = ["customSetLabel"]
extra_exact_ignores = ["My App Name"]
```

Precedence is **CLI > profile > default**: `security --profile portal` uses
`security_tools`/`security_fail_on` unless `--tools`/`--fail-on` are passed;
`analyze --profile portal` runs `linters`, `metadata_rules` and the `fail_on`
security gate.

## ⚠️ Technical Limitations

This tool performs **Static Analysis** (AST & Regex parsing). It does **not** execute your code or load QGIS libraries.
- **Dynamic Imports**: Imports inside functions or conditional blocks might be analyzed differently than top-level imports.
- **Runtime Validation**: Checks like "Missing Resources" rely on static string analysis of `.qrc` files and path strings. It cannot verify resources loaded dynamically at runtime.
- **False Positives**: While we strive for accuracy, complex meta-programming or unusual patterns might trigger false positives. Use `# noqa` or `.analyzerignore` to handle these cases.
- **Optional external tools**: Flake8, Bandit and detect-secrets are not bundled. Install `qgis-analyzer[flake8]`, `[security]` or `[portal]`; when a requested tool is missing, the report sets `tool_unavailable` (and `security` exits `2`) instead of reporting a silent zero.

## ⌨️ Full CLI Reference

> **Note**: The Python package is named `qgis-plugin-analyzer`, but the command-line tool is installed as `qgis-analyzer`.

### `qgis-analyzer analyze [scope] [path]`
Audits an existing QGIS plugin repository with optional specialized scopes.

**NEW in v1.9.0:** Specialized analysis scopes for targeted auditing.

**Available Scopes:**
- `i18n` - Internationalization and translation audit (detects untranslated strings)
- `security` - Security vulnerability scanning (unsafe calls, hardcoded secrets, SQL injection)
- `performance` - Performance and UI blocking detection (blocking loops, missing indexes)
- `architecture` - Dependency and coupling analysis (imports, QGIS API usage)
- `metadata` - QGIS metadata validation (metadata.txt compliance)
- `all` or no scope - Full analysis (default, legacy compatible)

**Arguments:**

| Argument | Description | Default |
| :--- | :--- | :--- |
| `scope` | **(Optional)** Analysis scope: `i18n`, `security`, `performance`, `architecture`, `metadata`, or `all`. | `all` |
| `project_path` | **(Required)** Path to the plugin directory to analyze. | `.` |
| `--scope SCOPE` | Explicit scope alternative to the positional form. | none |
| `--exclude PATTERN` | Extra ignore pattern (repeatable/comma-separated; `!` re-includes). | none |
| `-o`, `--output` | Directory where HTML/Markdown reports will be saved. | `./analysis_results` |
| `-r`, `--report` | Explicitly generate detailed HTML/Markdown reports. | `False` |
| `-p`, `--profile`| Configuration profile from `pyproject.toml` (`default`, `release`). | `default` |
| `--json` | Emit machine-readable JSON (`project_context.json`) to stdout. | `False` |
| `--include-content` | Embed module source content in the JSON output. | `False` |
| `--linters LIST` | Comma-separated lint tools (`ruff`, `flake8`; use `none` to disable). | `ruff` |
| `--flake8` | Shorthand for `--linters ruff,flake8`. | `False` |
| `--max-cc N` | Fail analysis if any function exceeds this cyclomatic complexity. | off |
| `--workers N` | Number of parallel worker processes (clamped to `1..4` to bound memory). | `min(4, cpu-1)` |
| `--no-cache` | Disable the incremental per-file analysis cache. | `False` |

**Ignore files and exclusions**

The matcher is ordered and **last match wins**, so a later `!pattern` re-includes a path:

`defaults` → `.gitignore` → `.qgisignore` → `.analyzerignore` → `--exclude` / profile `exclude`.

Default excludes include `docs/`, `tests/`, `.venv/`, `build/`, `dist/`, caches and
generated artifacts. To analyze one of those directories again:

```bash
qgis-analyzer analyze . --exclude '!docs/'
qgis-analyzer analyze . --exclude '!tests/'
```

**Examples:**
```bash
# Full analysis (legacy compatible)
qgis-analyzer analyze .
qgis-analyzer analyze /path/to/plugin

# Specialized i18n analysis (both forms are equivalent)
qgis-analyzer analyze i18n .
qgis-analyzer analyze . --scope i18n

# Analyze docs/ and tests/ explicitly
qgis-analyzer analyze . --exclude '!docs/' --exclude '!tests/'

# Security-only scan with reports
qgis-analyzer analyze security . --report
```

### `qgis-analyzer fix`
Automatically fix common QGIS issues identified during analysis.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `path` | **(Required)** Path to the plugin directory. | N/A |
| `--dry-run` | Show proposed changes without applying them. | `True` |
| `--apply` | Apply fixes to the files (disables dry-run). | `False` |
| `--auto-approve`| Apply fixes without interactive confirmation. | `False` |
| `--rules` | Comma-separated list of rule IDs to fix. | Fix all |
| `-o`, `--output` | Directory to read previous analysis from. | `./analysis_results` |

### `qgis-analyzer summary`
Shows a professional, color-coded summary of findings directly in your terminal.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `-b`, `--by` | Granularity of the summary: `total`, `modules`, `functions`, `classes`, `security`. | `total` |
| `-i`, `--input` | Path to the `project_context.json` file to summarize. | `analysis_results/project_context.json` |

### `qgis-analyzer security`
Performs a focused security scan on a file or directory.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `path` | **(Required)** Path to the file or directory to scan. | N/A |
| `--deep` | Enable the native entropy heuristic (full secret detection). | `False` |
| `--tools LIST` | Comma-separated tools: `native`, `bandit`, `detect-secrets`, `flake8`. | `native` |
| `--json` | Emit a machine-readable security report (findings, summary, tool status). | `False` |
| `--fail-on SEV` | Lowest severity that fails: `critical`, `warning`, `info`, `none`. | `critical` |
| `--exclude PATTERN` | Extra ignore pattern (repeatable/comma-separated; `!` re-includes). | none |
| `-p`, `--profile`| Configuration profile. | `default` |

**Examples:**
```bash
# Native scan (regex + AST rules); entropy only with --deep
qgis-analyzer security .

# Portal parity: real Bandit + detect-secrets + Flake8, JSON, block on critical findings
qgis-analyzer security . --tools bandit,detect-secrets,flake8 --json --fail-on critical

# Machine-readable native report
qgis-analyzer security . --deep --json
```

Exit codes: `0` clean, `1` findings at/above `--fail-on`, `2` invalid input or an unavailable requested tool.

### `qgis-analyzer version`
Shows the current version of the analyzer.

**Example:**
```bash
# Executive summary
qgis-analyzer summary

# Identify high-complexity functions
qgis-analyzer summary --by functions
```

### `qgis-analyzer list-rules`
Displays the full catalog of implemented QGIS audit rules with their severity and descriptions.

### `qgis-analyzer graph`
Visualizes the project's dependency graph.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `project_path` | Path to the plugin directory. | `.` |
| `--format` | Output format: `text` or `mermaid`. | `text` |

### `qgis-analyzer serve`
Starts a local web server to view the generated HTML reports.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `path` | Path to the analysis results directory. | `./analysis_results` |
| `--port` | Port to run the server on. | `8000` |

### `qgis-analyzer init`
Initializes a recommended `.analyzerignore` file in the current directory with common Python and QGIS development exclusions.


## 📊 Generated Reports

Written to the `--output` directory (default `./analysis_results`):

- **`project_context.json`** — machine-readable contract (schema v1):
  - Top level: `schema`/`schema_version`, `analyzer_version`, `project_name`, `project_path`, `analyzed_at`, `metrics`.
  - `ruff_findings` + `ruff_metadata` (`exit_code`, `tool_unavailable`, `command`).
  - `flake8_findings` + `flake8_metadata` (same fields plus `formatter`) when `--flake8`/`--linters` includes Flake8.
  - `repository_compliance` includes `constraint_errors` (blocking, e.g. binaries) and `constraint_warnings` (informational size).
  - `patterns` (design patterns) and `optimizations` (`module_too_large`, `complexity_refactoring`).
  - Per module: `path`, `lines`, `complexity`, `imports`, `functions`, `classes`, `ast_issues`, `research_metrics` (type-hint/docstring coverage, `halstead`).
  - `cc_gate` / `cc_violations` when `--max-cc` is used with `--json`.
  - `security --json` emits its own envelope: `schema`/`schema_version`, `analyzer_version`, `command`, `scope`, `tools`, `tool_status`, `tool_unavailable`, `findings` (`portal_severity`, `blocking`, `tool`), `summary` and `exit_code`.
- **`PROJECT_SUMMARY.md`** / **`PROJECT_SUMMARY.html`** — human-readable report.
- **`analyzer.log`** — run log.

> The JSON is consumed by `ai-context-core`; keep the schema keys stable (bump `schema_version` on change).

## 📜 Audit Rules

For a complete list of all implemented checks, their severity, and recommendations, please refer to the:

👉 **[Detailed Rules Catalog (RULES.md)](RULES.md)**

## 📚 References and Standards

The development of this analyzer is based on official QGIS community guidelines, geospatial standards, and industry best practices:

### Official QGIS Documentation
- **[PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)**: The primary resource for PyQGIS API usage and standards.
- **[QGIS Plugin Repository Requirements](https://plugins.qgis.org/publish/)**: Mandatory criteria for plugin approval in the official repository.
- **[QGIS Coding Standards](https://docs.qgis.org/latest/en/docs/developer_guide/codingstandards.html)**: Core style and organization guidelines for the QGIS project.
- **[QGIS HIG (Human Interface Guidelines)](https://docs.qgis.org/latest/en/docs/developer_guide/hig.html)**: Standards for consistent and accessible user interface design.
- **[QGIS Security Scanning Documentation](https://plugins.qgis.org/docs/security-scanning)**: Official guide on automated security analysis (Bandit, detect-secrets) for plugins.

### Industry & Community Standards
- **[flake8-qgis Rules](https://github.com/osgeosuomi/flake8-qgis)**: Community-driven linting rules for PyQGIS (QGS101-412).
- **[PEP 8 Style Guide](https://peps.python.org/pep-0008/)**: The fundamental style guide for Python code.
- **[PEP 257 Docstring Conventions](https://peps.python.org/pep-0257/)**: Standards for docstring structure and content.
- **[Maintainability Index (SEI)](https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-maintainability-index-range-and-meaning)**: Methodology for measuring software maintainability.
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Standard for clear, machine-readable commit history.
- **[Keep a Changelog](https://keepachangelog.com/)**: Best practices for maintainable version history.

### Security Standards
- **[Bandit (PyCQA)](https://bandit.readthedocs.io/)**: The security rules implemented (B1xx - B6xx) are directly derived from the Bandit project's rule set for identifying common security issues in Python code.
- **[CWE (Common Weakness Enumeration)](https://cwe.mitre.org/)**: Security findings are mapped to standard CWE IDs (e.g., CWE-78 Command Injection, CWE-89 SQL Injection) for industry-standard classification.
- **[OWASP Top 10](https://owasp.org/www-project-top-ten/)**: The "Hardcoded Secret" and "Injection" checks align with critical OWASP vulnerabilities.

### Internal Resources
- **[Detailed Rules Catalog](RULES.md)**: Full documentation of all audit rules implemented in this analyzer.
- **[Standardized Scoring Metrics](docs/development/SCORING_STANDARDS.md)**: Mathematical logic and thresholds for project evaluation.
- **[Project Roadmap](docs/development/ROADMAP.md)**: Current status and future plans for the analyzer.
- **[Release Process](docs/releases/RELEASE_PROCESS.md)**: How to cut a release — versioning, GitHub Release and PyPI publication.
- **[Comparison vs Alternatives](docs/research/COMPARISON_VS_ALTERNATIVES.md)**: Internal positioning notes (kept out of this README).
- **[Documentation Folder](docs/)**: Historical release notes, competitive analysis, and modernization guides.

## 🛠️ Contributing

Contributions are welcome! Please refer to our **[Contributing Guide](CONTRIBUTING.md)** to learn how to report bugs, propose rules, and submit code changes.

Audit rules are located in `src/analyzer/rules/` (regex catalog) and `src/analyzer/visitors/` (AST visitors). Feel free to add new rules following the existing pattern!

---
## ⚖️ License

This project is licensed under the **GNU General Public License v3 (GPL v3)**. See the [LICENSE](LICENSE) file for details.

---
*Developed for the SecInterp team and the QGIS community.*
