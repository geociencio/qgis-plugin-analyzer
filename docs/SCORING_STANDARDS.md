# Standardized Scoring Metrics

This document outlines the objective criteria used to evaluate Python projects and QGIS plugins in this tool.

## 1. Code Maintainability & Complexity

We use a combination of the **Maintainability Index (MI)** and **Cyclomatic Complexity (CC)**.

### 1.1 Maintainability Index (MI)
Based on the SEI formula used by tools like Radon:
`MI = max(0, (171 - 0.23 * CC - 16.2 * ln(SLOC)) * 100 / 171)`

*   **CC (Cyclomatic Complexity)**: Measures decision points (ifs, loops, etc.).
*   **SLOC (Source Lines of Code)**: Measures executable volume.

### 1.2 Python Standards (PEP 8 & PEP 257)
Compliance is measured by penalizing deviations detected by **Ruff**, following the Pylint scoring model:

| Category | Weight | Description |
| :--- | :--- | :--- |
| **Error (E/F)** | 5.0 | Critical bugs, syntax errors, undefined names. |
| **Warning (W)** | 1.0 | Potential bugs or risky patterns. |
| **Refactor (R)** | 1.0 | Code smells (e.g., too many arguments). |
| **Convention (C)** | 1.0 | PEP 8 style violations (naming, whitespace). |

**Formula:**
`Lint Score = 10 - ((5*E + W + R + C) / total_statements) * 10`

## 2. Structural Stability & Best Practices

Stability is measured by the interdependence of modules and adherence to **PEP 257**:

*   **Circular Dependencies**: Strictly penalized (-10 points per cycle).
*   **Docstrings (PEP 257)**: Essential for maintainability. Missing module/class docstrings are flagged as `Convention` issues.
*   **Coupling**: High "Fan-Out" (one module depending on many others) reduces the modularity score.

## 3. QGIS Compliance (Plugin Mode Only)

For QGIS plugins, the score reflects adherence to the [Official QGIS Plugin Standards](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/plugins/index.html).

| Rule Category | Severity | Penalty |
| :--- | :--- | :--- |
| **Security / Stability** | High | -20 pts |
| **Legacy / Obsolete API** | Medium | -10 pts |
| **Best Practices (i18n, icons)** | Low | -5 pts |
| **Repository Structure** | Critical | -30 pts |

## 4. Grading Scale

Regardless of the project, we adhere to the standard academic/industry grading scale:

*   **90 - 100**: **A** (Excellent)
*   **80 - 89**: **B** (Good)
*   **60 - 79**: **C** (Needs improvement)
*   **< 60**: **D/F** (Critical technical debt)
