# 🛡️ Detailed Commands Guide (GIS) - QGIS Plugin Analyzer

The **QGIS Plugin Analyzer** is an advanced auditing tool designed to ensure that QGIS (PyQGIS) plugins meet the highest standards of quality, security, and maintainability. This guide details every available command, its parameters, and recommended usage scenarios.

---

## 📋 CLI Command Reference

The main command is `qgis-analyzer`. Its subcommands are detailed below:

### 1. `analyze` (The Audit Engine)
Performs an exhaustive analysis of a project, generating complexity metrics, stability scores, and detecting QGIS-specific issues.

**Base Usage:**
```bash
qgis-analyzer analyze /path/to/plugin
```

**Main Parameters:**
- `-o, --output`: Output directory for reports (default: `./analysis_results`).
- `-r, --report`: Generates detailed HTML and Markdown reports.
- `-p, --profile`: Specifies the configuration profile in `pyproject.toml` (e.g., `default`, `release`).

> [!TIP]
> If you run `qgis-analyzer /path/to/plugin` without a subcommand, the system automatically assumes the `analyze` command.

---

### 2. `fix` (Automated Correction)
Your code's "Guardian Angel." It allows for the automatic correction of common issues detected by audit rules.

**Base Usage:**
```bash
qgis-analyzer fix /path/to/plugin
```

**Control Options:**
- `--dry-run`: (Enabled by default) Shows proposed changes without applying them.
- `--apply`: Executes modifications directly to the files.
- `--auto-approve`: Applies all changes without interactive confirmation.
- `--rules`: Filters which rules to fix (e.g., `--rules QGS101,QGS105`).

---

### 3. `summary` (Executive Summary)
Ideal for getting a quick overview of project health directly in the terminal without opening external reports.

**Base Usage:**
```bash
qgis-analyzer summary
```

**Granularity Levels (`-b, --by`):**
- `total`: (Default) An overall summary of the entire project.
- `modules`: Breakdown by Python files.
- `classes`: Analysis of class complexity.
- `functions`: Identification of functions with high technical debt.

---

### 4. `list-rules` (Rules Catalog)
Displays the full list of implemented audit rules, their severity, and associated error messages.

**Usage:**
```bash
qgis-analyzer list-rules
```

---

### 5. `init` (Quick Configuration)
Creates an `.analyzerignore` file in the current directory with exclusion patterns recommended by the community (venvs, caches, builds, etc.).

**Usage:**
```bash
qgis-analyzer init
```

---

## 🚀 Usage Scenarios (Practical Cases)

### A. Pre-release Audit
Before uploading your plugin to the [Official QGIS Plugin Repository](https://plugins.qgis.org/), use the `release` profile to ensure strict compliance.

```bash
qgis-analyzer analyze . -p release -r
```
*   **What it checks:** Prohibited binaries, package size, metadata URL validity in `metadata.txt`, and strict standard adherence.

### B. Continuous Integration (CI/CD)
Integrate the analyzer into GitHub Actions to block PRs that introduce circular dependencies or high complexity.

```yaml
- name: Run Quality Check
  run: qgis-analyzer analyze . --profile release
```

### C. Legacy Code Refactoring
Working on an old plugin? Use `summary --by functions` to quickly identify the most complex parts of the code.

```bash
qgis-analyzer summary --by functions
```

---

## ⚙️ Advanced Customization

### `pyproject.toml` File
Define custom profiles to adapt the analysis rigor:

```toml
[tool.qgis-analyzer.profiles.my_profile]
strict = true
fail_on_error = true
[tool.qgis-analyzer.profiles.my_profile.rules]
QGS101 = "error"   # Strictly forbid direct GDAL imports
QGS303 = "ignore"  # Ignore icon validation for now
```

### `.analyzerignore` File
Use this file to exclude folders that should not be analyzed (e.g., external libraries or compressed data files).

---
*Documentation generated for the PyQGIS community.*
