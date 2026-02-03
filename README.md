# QGIS Plugin Analyzer 🛡️

👉 **[View Full Rules Catalog (RULES.md)](RULES.md)**
![GitHub release (latest by date)](https://img.shields.io/github/v/release/geociencio/qgis-plugin-analyzer?color=blue&logo=github)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?logo=git)
![Quality Score](https://img.shields.io/badge/Module%20Stability-92.3%2F100-brightgreen)
![Maintainability](https://img.shields.io/badge/Maintainability-84.1%2F100-green)
![Security Score](https://img.shields.io/badge/Security--Bandit-98.7%2F100-brightgreen)

The **QGIS Plugin Analyzer** is a static analysis tool designed specifically for QGIS (PyQGIS) plugin developers. Its goal is to elevate plugin quality by ensuring they follow community best practices and are optimized for AI-assisted development.

## ✨ Main Features

- **Security Core (Bandit-inspired)**: Professional vulnerability scanning detecting `eval`, `exec`, shell injections, and SQL injection risks.
- **Deep Entropy Secret Scanner**: Detects hardcoded API keys, passwords, and sensitive tokens using regex and information entropy.
- **High-Performance Engine**: Parallel analysis powered by `ProcessPoolExecutor` for ultra-fast execution on multi-core systems.
- **Project Auto-Detection**: Intelligently distinguishes between official QGIS Plugins and Generic Python Projects, tailoring validation logic accordingly.
- **Advanced Ignore Engine**: Robust `.analyzerignore` support with non-anchored patterns and smart default excludes (`.venv`, `build`, etc.).
- **Deep Semantic Analysis**: Cross-file dependency graphing, circular import detection, and module coupling metrics.
- **Interactive Auto-Fix Mode**: Automatically fix common QGIS issues (GDAL imports, PyQt bridge, logging, i18n) with safety checks.
- **Official Repository Compliance**: Proactive validation of binaries, package size, and metadata URLs.
- **Real-time Progress**: CLI feedback with a progress bar and ETA tracking.
- **Enhanced Configuration Profiles**: Rule-level severity control (`error`, `warning`, `info`, `ignore`) via `pyproject.toml`.
- **Integrated Ruff Analysis**: Combines custom QGIS rules with the fastest linter in the Python ecosystem.
- **Qt Resource Validation**: Detect missing or broken resource paths (`:/plugins/...`) in your code.
- **Signal/Slot Safety**: Detection of potentially missing slots or inherited slot warnings.
- **AI-Ready**: Generates structured summaries and optimized contexts for LLMs.
- **Zero Runtime Dependencies**: Works using only the Python standard library (Ruff as an external tool).

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

**1. Analyze a Plugin:**
```bash
qgis-analyzer analyze /path/to/your/plugin -o ./quality_report
```

**2. Auto-Fix issues (Dry Run):**
```bash
qgis-analyzer fix /path/to/your/plugin
```

**3. Legacy Support:**
The default command remains analysis if no subcommand is specified:
```bash
qgis-analyzer /path/to/your/plugin
```

## 🔄 Pre-commit Hook

You can run `qgis-plugin-analyzer` automatically before every commit to ensure quality. Add this to your `.pre-commit-config.yaml`:

```yaml
  - repo: https://github.com/geociencio/qgis-plugin-analyzer
    rev: v1.5.0  # Use the latest tag
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

### `qgis-analyzer analyze`
Audits an existing QGIS plugin repository.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `project_path` | **(Required)** Path to the plugin directory to analyze. | N/A |
| `-o`, `--output` | Directory where HTML/Markdown reports will be saved. | `./analysis_results` |
| `-p`, `--profile`| Configuration profile from `pyproject.toml` (`default`, `release`). | `default` |

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

### Industry & Community Standards
- **[flake8-qgis Rules](https://github.com/qgis/flake8-qgis)**: Community-driven linting rules for PyQGIS (QGS101-106).
- **[PEP 8 Style Guide](https://peps.python.org/pep-0008/)**: The fundamental style guide for Python code.
- **[PEP 257 Docstring Conventions](https://peps.python.org/pep-0257/)**: Standards for docstring structure and content.
- **[Maintainability Index (SEI)](https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-maintainability-index-range-and-meaning)**: Methodology for measuring software maintainability.
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Standard for clear, machine-readable commit history.
- **[Keep a Changelog](https://keepachangelog.com/)**: Best practices for maintainable version history.

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
