# Internal: Comparison vs Alternatives

> **Internal document** (removed from the public `README.md` to keep it focused).
> Positioning notes comparing `qgis-plugin-analyzer` with `flake8-qgis`, plain
> `ruff` and the official QGIS plugin repository bot.

| Feature | **QGIS Plugin Analyzer** | flake8-qgis | Ruff (Standard) | Official Repo Bot |
| :--- | :---: | :---: | :---: | :---: |
| **Run Locally / Offline** | ✅ (Your Machine) | ✅ | ✅ | ❌ (Upload Only) |
| **Static Linting** | ✅ (Ruff + Custom) | ✅ (flake8) | ✅ (General) | ✅ (Limited) |
| **QGIS-Specific Rules** | ✅ (Precise AST) | ✅ (Regex/AST) | ❌ | ✅ |
| **Interactive Auto-Fix** | ✅ | ❌ | ❌ | ❌ |
| **Semantic Analysis** | ✅ | ❌ | ❌ | ❌ |
| **Security Audit** | ✅ (Bandit-style) | ❌ | ❌ | ✅ (Server-side) |
| **Secret Scanning** | ✅ (Entropy) | ❌ | ❌ | ✅ (Server-side) |
| **HTML/MD Reports** | ✅ | ❌ | ❌ | ❌ |
| **AI Context Gen** | ✅ (Project Brain) | ❌ | ❌ | ❌ |

## Key Differentiators

1. **Shift Left (Run Locally)**: The biggest advantage is being able to run the
   **same high-standard checks** as the Official Repository *before* you upload
   your plugin. No more "reject-fix-upload" loops.
2. **High-Performance Hybrid Engine**: Combines multi-core AST processing with
   deep understanding of cross-file relationships and Qt-specific patterns.
3. **Safety-First Auto-Fixing**: AST-based transformations with Git status
   verification and interactive diff previews.
4. **Zero Runtime Stack**: Minimal footprint, ultra-fast execution, and easy CI
   integration.
5. **AI-Centric Design**: Built to help developers and AI agents understand
   complex QGIS plugins instantly.

## Cross-tool notes (ecosystem)

- `ai-context-core` consumes `analysis_results/project_context.json` (schema v1);
  the analyzer owns the *context* contract only (ADR-0008).
- `qgis-plugin-manager` delegates security/analysis to the analyzer CLI; the
  analyzer stays read-only (no packaging/deploy/compile).
