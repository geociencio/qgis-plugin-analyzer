# Bug Report: `qgis-plugin-analyzer` Type Hint Coverage Fails on Multi-Line Signatures

## 🐛 Description
It was initially reported that the `qgis-plugin-analyzer` CLI tool incorrectly reported an artificially low **Type Hint Coverage (Returns)** metric for Python projects that use code formatters like `black` or strictly wrap long lines (e.g. reporting 44.7% instead of 89.0%).

## 🔍 Root Cause Analysis
Upon thorough investigation of the `src/analyzer/visitors/metrics_visitor.py` codebase, two key findings emerged:

1. **Misconception around Regular Expressions:** The analyzer **does not** use regex or line-by-line parsing for detecting type hints. The underlying engine properly uses Python's native `ast` module (`ast.FunctionDef.returns`), which natively handles multi-line signatures formatted by `black`. Exact reproductions of the failing multi-line scripts confirmed 100% accurate coverage calculation.
2. **The True Cause (Async Omission):** The actual reason for the drastic coverage disparity in modern QGIS plugins (like `sec_interp`) was the omission of `ast.AsyncFunctionDef` support in the `MetricsVisitor`. While independent AST scans evaluated all function types, the core analyzer only evaluated synchronous `def` functions, skipping async operations entirely. This heavily skewed the metric counts.

## 🛠️ Resolution Implemented

### Updated to Capture Async Signatures
The `metrics_visitor.py` module was updated. `visit_AsyncFunctionDef` was added to capture async functions, explicitly delegating to the existing type hint calculation logic. Helper method signatures were also updated to process both `ast.FunctionDef` and `ast.AsyncFunctionDef`.

### Benefits of the Fix
1. **Accurate Coverage:** All functions, both standard synchronous and asynchronous PyQGIS background tasks, are accurately included in the coverage calculation.
2. **Formatting Agnostic:** The AST metrics engine continues to cleanly handle complex, multi-line definitions without regex flaws.
