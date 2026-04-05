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

**Quality Metrics:**

![Module Stability](https://img.shields.io/badge/Module%20Stability-45.1%2F100-orange?style=flat-square)
![Maintainability](https://img.shields.io/badge/Maintainability-90.0%2F100-brightgreen?style=flat-square)
![Security Score](https://img.shields.io/badge/Security--Bandit-100.0%2F100-brightgreen?style=flat-square)
![Type Coverage](https://img.shields.io/badge/Type%20Hints%20(Params)-97.1%25-brightgreen?style=flat-square)
![Docstring Coverage](https://img.shields.io/badge/Docstrings-77.9%25-green?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-49%2F49%20passing-brightgreen?style=flat-square&logo=pytest)

The **QGIS Plugin Analyzer** is a static analysis tool designed specifically for QGIS (PyQGIS) plugin developers. Its goal is to elevate plugin quality by ensuring they follow community best practices and are optimized for AI-assisted development.

## ✨ Main Features

- **Security Core (Bandit-inspired)**: Professional vulnerability scanning detecting `eval`, `exec`, shell injections, and SQL injection risks.
- **Deep Entropy Secret Scanner**: Detects hardcoded API keys, passwords, and sensitive tokens using regex and information entropy.
- **High-Performance Engine**: Parallel analysis powered by `ProcessPoolExecutor` with single-pass AST traversal and shared worker context.
- **Project Auto-Detection**: Intelligently distinguishes between official QGIS Plugins and Generic Python Projects, tailoring validation logic accordingly.
- **Advanced Ignore Engine**: Robust `.analyzerignore` support with non-anchored patterns and smart default excludes (`.venv`, `build`, etc.).
- **Deep Semantic Analysis**: Cross-file dependency graphing (Mermaid), circular import detection, and module coupling metrics.
- **Interactive Auto-Fix Mode**: Automatically fix common QGIS issues (GDAL imports, PyQt bridge, logging, i18n) with safety checks.
- **Official Repository Compliance**: Proactive validation of binaries, package size, and metadata URLs.
- **Real-time Progress**: CLI feedback with a progress bar and ETA tracking.
- **Enhanced Configuration Profiles**: Rule-level severity control (`error`, `warning`, `info`, `ignore`) via `pyproject.toml`.
- **Integrated Ruff Analysis**: Combines custom QGIS rules with the fastest linter in the Python ecosystem.
- **Qt Resource Validation**: Detect missing or broken resource paths (`:/plugins/...`) in your code.
- **Extended Safety Audit**: Detection of signal leaks, missing slots, and UI-blocking loops (QgsTask suggestions).
- **Embedded Web Server**: View reports instantly with the built-in `serve` command.
- **AI-Ready**: Generates structured summaries and optimized contexts for LLMs.
- **Zero Runtime Dependencies**: Works using only the Python standard library (Ruff as an external tool).

## 🆕 What's New in v1.11.0

**Robust Project Discovery & Dynamic Versioning** - Major improvements to the core engine and project identification logic:

- 📁 **Bulletproof Project Detection** - Fixed a critical issue where QGIS plugins were incorrectly identified as generic projects if `metadata.txt` was listed in `.analyzerignore`. Metadata detection now correctly prioritizes plugin identification over ignore rules.
- 🔄 **Dynamic Versioning** - The analyzer now uses a dynamic versioning system that automatically stays in sync with `pyproject.toml`, ensuring accuracy across all interfaces without hardcoded values.
- 🧹 **Clean Analysis Logs** - Removed redundant project type reporting to provide a more focused and professional terminal output.

**From v1.10.1:**
- ⚡ **Async Support** - Full AST support for `AsyncFunctionDef` in metrics calculations.

[**📖 Full Release Notes**](docs/releases/notes/v1.11.0.md) | [**🗺️ CLI Commands Roadmap**](docs/research/CLI_COMMANDS_ROADMAP.md)

## ⚖️ Why use this Analyzer? (Comparison)

| Feature | **QGIS Plugin Analyzer** | flake8-qgis | Ruff (Standard) | Official Repo Bot |
| :--- | :---: | :---: | :---: | :---: |
| **Run Locally / Offline**| ✅ (Your Machine) | ✅ | ✅ | ❌ (Upload Only) |
| **Static Linting** | ✅ (Ruff + Custom) | ✅ (flake8) | ✅ (General) | ✅ (Limited) |
| **QGIS-Specific Rules**| ✅ (Precise AST) | ✅ (Regex/AST) | ❌ | ✅ |
| **Interactive Auto-Fix**| ✅ | ❌ | ❌ | ❌ |
| **Semantic Analysis**  | ✅ | ❌ | ❌ | ❌ |
| **Security Audit**     | ✅ (Bandit-style) | ❌ | ❌ | ✅ (Server-side) |
| **Secret Scanning**    | ✅ (Entropy) | ❌ | ❌ | ✅ (Server-side) |
| **HTML/MD Reports**    | ✅ | ❌ | ❌ | ❌ |
| **AI Context Gen**      | ✅ (Project Brain) | ❌ | ❌ | ❌ |

### Key Differentiators

1.  **Shift Left (Run Locally)**: The biggest advantage is being able to run the **same high-standard checks** as the Official Repository *before* you upload your plugin. No more "reject-fix-upload" loops.
2.  **High-Performance Hybrid Engine**: Combines multi-core AST processing with deep understanding of cross-file relationships and Qt-specific patterns.
3.  **Safety-First Auto-Fixing**: AST-based transformations with Git status verification and interactive diff previews.
4.  **Zero Runtime Stack**: Minimal footprint, ultra-fast execution, and easy CI integration.
5.  **AI-Centric Design**: Built to help developers and AI agents understand complex QGIS plugins instantly.

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

**2. Local installation for development:**
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

[tool.qgis-analyzer.profiles.release]
strict = true
fail_on_error = true

[tool.qgis-analyzer.profiles.default.rules]
QGS101 = "error"    # Ban specific module imports
QGS105 = "warning"  # Warn on iface usage
QGS303 = "ignore"   # Ignore resource path checks
```

## ⚠️ Technical Limitations

This tool performs **Static Analysis** (AST & Regex parsing). It does **not** execute your code or load QGIS libraries.
- **Dynamic Imports**: Imports inside functions or conditional blocks might be analyzed differently than top-level imports.
- **Runtime Validation**: Checks like "Missing Resources" rely on static string analysis of `.qrc` files and path strings. It cannot verify resources loaded dynamically at runtime.
- **False Positives**: While we strive for accuracy, complex meta-programming or unusual patterns might trigger false positives. Use `# noqa` or `.analyzerignore` to handle these cases.

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
| `-o`, `--output` | Directory where HTML/Markdown reports will be saved. | `./analysis_results` |
| `-r`, `--report` | Explicitly generate detailed HTML/Markdown reports. | `False` |
| `-p`, `--profile`| Configuration profile from `pyproject.toml` (`default`, `release`). | `default` |

**Examples:**
```bash
# Full analysis (legacy compatible)
qgis-analyzer analyze .
qgis-analyzer analyze /path/to/plugin

# Specialized i18n analysis
qgis-analyzer analyze i18n .

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
| `-b`, `--by` | Granularity of the summary: `total`, `modules`, `functions`, `classes`. | `total` |
| `-i`, `--input` | Path to the `project_context.json` file to summarize. | `analysis_results/project_context.json` |

### `qgis-analyzer security`
Performs a focused security scan on a file or directory.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `path` | **(Required)** Path to the file or directory to scan. | N/A |
| `--deep` | Run more intensive (but slower) security checks. | `False` |
| `-p`, `--profile`| Configuration profile. | `default` |

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

- `project_context.json`: Full structured data for external integrations.

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
- **[flake8-qgis Rules](https://github.com/qgis/flake8-qgis)**: Community-driven linting rules for PyQGIS (QGS101-106).
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
- **[Standardized Scoring Metrics](docs/SCORING_STANDARDS.md)**: Mathematical logic and thresholds for project evaluation.
- **[Project Roadmap](docs/ROADMAP.md)**: Current status and future plans for the analyzer.
- **[Documentation Folder](docs/)**: Historical release notes, competitive analysis, and modernization guides.

## 🛠️ Contributing

Contributions are welcome! Please refer to our **[Contributing Guide](CONTRIBUTING.md)** to learn how to report bugs, propose rules, and submit code changes.

Audit rules are located in `src/analyzer/scanner.py`. Feel free to add new rules following the existing pattern!

---
## ⚖️ License

This project is licensed under the **GNU General Public License v3 (GPL v3)**. See the [LICENSE](LICENSE) file for details.

---
*Developed for the SecInterp team and the QGIS community.*
