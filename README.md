# QGIS Plugin Analyzer 🛡️

The **QGIS Plugin Analyzer** is a static analysis tool designed specifically for QGIS (PyQGIS) plugin developers. Its goal is to elevate plugin quality by ensuring they follow community best practices and are optimized for AI-assisted development.

## ✨ Main Features

- **QGIS Standards Audit**: Detects missing internationalization (i18n), obsolete APIs, and unsafe threading. See [Rule Catalog](RULES.md).
- **Architecture Analysis**: Identifies violations in separation of responsibilities (Core vs GUI).
- **Quality Metrics**: Calculates cyclomatic complexity and documentation coverage.
- **AI-Ready**: Generates structured summaries and optimized contexts for LLMs.
- **High Performance**: Uses parallel processing to analyze large projects in seconds.
- **Selective Auditing**: Support for `.analyzerignore` to exclude specific files or directories from analysis.

## ⚖️ Why use this Analyzer? (Comparison)

| Feature | QGIS Plugin Analyzer | flake8-qgis | qgis-plugin-dev-tools | Official Repo Bot |
| :--- | :---: | :---: | :---: | :---: |
| **Static Linting** | ✅ (Custom Rules) | ✅ (Strict) | ❌ | ✅ (Limited) |
| **Complexity (AST)** | ✅ | ❌ | ❌ | ❌ |
| **QGIS i18n Audit** | ✅ | ❌ | ❌ | ✅ |
| **Architecture Audit**| ✅ (UI/Core) | ❌ | ❌ | ❌ |
| **Performance Rules** | ✅ (Spatial Index) | ✅ | ❌ | ❌ |
| **Security Scan** | ✅ | ❌ | ❌ | ✅ (Malware) |
| **AI Context Gen**| ✅ | ❌ | ❌ | ❌ |
| **Multiprocess Support**  | ✅ | ❌ | ❌ | ❌ |
| **External Reports**    | ✅ (MD, JSON) | ❌ | ✅ (Packaging) | ❌ |

### Key Differentiators

1.  **Holistic Quality Score**: Unlike linters that only report errors, the Analyzer provides a **Quality Score (0-100)**.
2.  **Native AI Infrastructure**: Generates a structured "Project Brain" that allows AI assistants (ChatGPT/Gemini) to provide much more accurate refactoring suggestions.
3.  **Architecture Compliance**: Detects pattern violations (e.g., heavy logic in the UI), the #1 cause of technical debt in plugins.
4.  **Total Independence**: Can be run on any project without being part of it, keeping the plugin repository clean.

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

### Run Analysis:
```bash
qgis-analyzer /path/to/your/plugin -o ./quality_report
```

## 📊 Generated Reports

- `PROJECT_SUMMARY.md`: Executive summary with quality score and critical findings.
- `project_context.json`: Full structured data for external integrations.

## 📚 References and Standards

The development of this analyzer is based on official QGIS community guidelines and industry standards:

- **[PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)**: The bible for Python plugin development.
- **[QGIS Plugin Repository Requirements](https://plugins.qgis.org/publish/)**: Official criteria for plugin approval in the official repository.
- **[QGIS Coding Standards](https://docs.qgis.org/latest/en/docs/developer_guide/codingstandards.html)**: Style and code organization standards for QGIS.
- **[QGIS HIG (Human Interface Guidelines)](https://docs.qgis.org/latest/en/docs/developer_guide/hig.html)**: Guide for designing consistent user interfaces.
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Standard for clear and structured commit messages.

## 🛠️ Contributing
Audit rules are located in `src/analyzer/scanner.py`. Feel free to add new rules following the existing pattern!

---
*Developed for the SecInterp team and the QGIS community.*
