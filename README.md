# QGIS Plugin Analyzer 🛡️
![GitHub release (latest by date)](https://img.shields.io/github/v/release/geociencio/qgis-plugin-analyzer?color=blue&logo=github)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/github/license/geociencio/qgis-plugin-analyzer?color=green)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?logo=git)

The **QGIS Plugin Analyzer** is a static analysis tool designed specifically for QGIS (PyQGIS) plugin developers. Its goal is to elevate plugin quality by ensuring they follow community best practices and are optimized for AI-assisted development.

## ✨ Main Features

- **Integrated Ruff Analysis**: Combines custom QGIS rules with the fastest linter in the Python ecosystem.
- **Boilerplate Generation (`init`)**: Creates professional plugin structures (`processing`, `gui`, `map_tool`) instantly.
- **AI-Ready**: Generates structured summaries and optimized contexts for LLMs.
- **HTML Reports**: Professional visualization of plugin health.
- **High Performance**: Parallel processing to analyze large projects in seconds.
- **Selective Auditing**: Support for `.analyzerignore` to exclude specific files or directories from analysis.

## ⚖️ Why use this Analyzer? (Comparison)

| Feature | **QGIS Plugin Analyzer** | flake8-qgis | Ruff (Standard) | Official Repo Bot |
| :--- | :---: | :---: | :---: | :---: |
| **Static Linting** | ✅ (Ruff + Custom) | ✅ (flake8) | ✅ (General) | ✅ (Limited) |
| **QGIS-Specific Rules**| ✅ (Precise AST) | ✅ (Regex/AST) | ❌ | ✅ |
| **Speed (Rust/Parallel)**| ✅ | ❌ | ✅ | ❌ |
| **Project Templating** | ✅ (`init`) | ❌ | ❌ | ❌ |
| **i18n / API Audit** | ✅ | ❌ | ❌ | ✅ |
| **Architecture Audit** | ✅ (UI/Core) | ❌ | ❌ | ❌ |
| **HTML/MD Reports** | ✅ | ❌ | ❌ | ❌ |
| **AI Context Gen** | ✅ (Project Brain) | ❌ | ❌ | ❌ |
| **Strict CI Profiles** | ✅ | ❌ | ✅ | ❌ |

### Key Differentiators

1.  **Maximum Performance Hybrid Engine**: Combines **Ruff's** Rust engine (for PEP8 rules) with our **AST** engine (for PyQGIS rules), offering up to 100x speed over traditional linters.
2.  **Intelligent Boilerplate Generation**: Unlike other tools focused solely on analysis, the `init` command allows creating "AI-Ready" plugins from day one.
3.  **Architecture Audit**: Unique in detecting pattern violations (like heavy logic in the UI), the #1 cause of technical debt in complex plugins.
4.  **AI Infrastructure (Project Brain)**: Generates optimized technical summaries so assistants like ChatGPT or Gemini understand your code instantly.
5.  **CI/CD Ready**: Configuration profiles allow integrating compliance failures directly into your GitHub Actions pipelines.

## 🚀 Installation and Usage

### Installation with `uv` (Recommended):

If you have [uv](https://github.com/astral-sh/uv) installed, you can install the analyzer quickly and in isolation:

**1. As a global tool (isolated):**
```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-analyzer.git
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

**2. Create a Plugin from Template:**
```bash
qgis-analyzer init my_new_plugin --type map_tool --name "Pro Tool"
```

**3. Legacy Support:**
The default command remains analysis if no subcommand is specified:
```bash
qgis-analyzer /path/to/your/plugin
```

## ⌨️ Full CLI Reference

### `qgis-analyzer analyze`
Audits an existing QGIS plugin repository.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `project_path` | **(Required)** Path to the plugin directory to analyze. | N/A |
| `-o`, `--output` | Directory where HTML/Markdown reports will be saved. | `./analysis_results` |
| `-p`, `--profile`| Configuration profile from `pyproject.toml` (`default`, `release`). | `default` |

### `qgis-analyzer init`
Generates a new QGIS plugin project structure from a template.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `path` | **(Required)** Destination path for the new project. | N/A |
| `-t`, `--type` | Template type: `processing`, `gui`, or `map_tool`. | `gui` |
| `--name` | Human-readable name of the plugin. | `My QGIS Plugin` |
| `--author` | Name of the lead developer. | `QGIS Developer` |
| `--email` | Contact email for the plugin. | `dev@qgis.org` |

## 📊 Generated Reports

- `PROJECT_SUMMARY.md`: Executive summary with quality score and critical findings.
- `project_context.json`: Full structured data for external integrations.

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
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Standard for clear, machine-readable commit history.
- **[Keep a Changelog](https://keepachangelog.com/)**: Best practices for maintainable version history.

### Internal Resources
- **[Detailed Rules Catalog](RULES.md)**: Full documentation of all audit rules implemented in this analyzer.

## 🛠️ Contributing
Audit rules are located in `src/analyzer/scanner.py`. Feel free to add new rules following the existing pattern!

---
*Developed for the SecInterp team and the QGIS community.*
