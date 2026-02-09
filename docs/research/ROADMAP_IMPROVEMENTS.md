# Roadmap: Future Improvements & Optimizations

This document outlines the strategic areas for improving the **QGIS Plugin Analyzer** beyond basic linting and scoring fixes.

## 1. Engine & Performance Optimizations [DONE]
- [x] **Single-Pass AST Traversal**: Refactored `CompositeVisitor` to perform a single traversal of the AST tree, dispatching nodes to sub-visitors using an optimized hook model.
- [x] **Worker Context Reuse**: Optimized `analyze_module_worker` using process-pool initializers to share heavyweight configuration and rules across parallel processes.
- [ ] **Subprocess Pooling**: Further optimize Ruff execution by potentially batching calls or using a daemon mode if latency becomes an issue for huge projects.

## 2. Advanced Code Metrics & Architecture
- [ ] **Cognitive Complexity (CC2)**: Implement or integrate Cognitive Complexity (Sonar-style) to better reflect human readability compared to standard McCabe complexity.
- [ ] **Module Instability ($I$)**: Calculate the instability metric ($I = FanOut / (FanIn + FanOut)$). This helps identify modules that are "too coupled" and hard to maintain.
- [ ] **Architecture Guards**: Implement custom rules to enforce package layering (e.g., "Core modules must not import from UI modules").
- [ ] **Project-Level Complexity Heatmap**: Generate a stats summary that highlights the "hottest" modules (high complexity + high coupling).

## 3. QGIS Standards & Best Practices (QGIS-specific) [DONE/ONGOING]
- [x] **Thread Safety Audit (`QgsTask`)**: Detected long-running loops (e.g., intensive `getFeatures()` or `requests`) that are *not* wrapped in a `QgsTask` (via `SafetyVisitor`).
- [x] **Signal/Slot Leak Detection**: Automatically verified that signals connected in `plugin.initGui()` are properly disconnected in `plugin.unload()`.
- [ ] **Layer Registry Audit**: Check for `QgsProject.instance().addMapLayer()` calls that might be missing proper cleanup or causing side effects in long-lived plugins.
- [ ] **Advanced Resource Usage Tracking**: Improve the reporting of *where* missing resources (from `semantic.py`) are used, including `.ui` and `.qml` file scanning.

## 4. Reporting & UX Enhancements [ONGOING]
- [x] **Dependency Graph Visualization**: Generated a `dependency_graph.mmd` (Mermaid) visualization for plugin architecture (via `graph` command).
- [ ] **Interactive HTML Reports**: Update the HTML reporter with sortable tables, collapsible code snippets, and a dashboard-style overview.
- [ ] **Local Report Server**: Implemented a `serve` command to easily view analysis results in a local browser.
- [ ] **Rich Terminal Output**: Use block characters (░▒▓█) for progress bars and distribution charts for better visual feedback.

---
*Updated by Antigravity on 2026-02-09*
