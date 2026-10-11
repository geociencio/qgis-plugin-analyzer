# Rule Catalog: QGIS Plugin Analyzer 📜

This document details the automatic audit rules implemented in the analyzer to ensure that plugins follow official QGIS standards and development best practices.

> **Source of truth**: regex-based QGIS rules are also listed by
> `qgis-plugin-analyzer list-rules`. AST/visitor rules (`MISSING_I18N`, Qt6
> migration, design/anti-pattern rules, …) are documented here; a unified rule
> registry that renders this file from code is tracked as a follow-up (Fase 6).

All rules support inline suppression via `# noqa` (suppress everything on the
line) or `# noqa: RULE_ID` (suppress a single rule).

## 1. Internationalization (i18n)

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MISSING_I18N` | 🔴 High | Detects user-facing string literals not wrapped in `self.tr()` or `QCoreApplication.translate()` (AST-based; excludes docstrings, technical strings and `# no-i18n` / `# noqa`). | Wrap strings in `self.tr("Text")` or `QCoreApplication.translate()`, or add `# no-i18n`. |

## 2. Obsolete API and Precision

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `OBSOLETE_API` | 🔴 High | Use of old methods like `writeAsVectorFormat()`. | Use the modern V3 version: `QgsVectorFileWriter.writeAsVectorFormatV3()`. |
| `OBSOLETE_VARIANT`| 🟡 Medium | Use of obsolete `QVariant` type constants (e.g., `QVariant.String`). | Use `QMetaType.Type.QString` or native types depending on the QGIS version. |
| `UNPRECISE_LAYER` | 🟡 Medium | Use of `mapLayersByName()`. | Use `mapLayers()` or unique layer IDs to avoid ambiguity with duplicate names. |

## 3. Threading Security & Safety
| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `UNSAFE_THREAD` | 🔴 High | Use of standard Python `threading.Thread`. | Use `QgsTask` or `QThread` to safely interact with the QGIS main thread. |
| ~~`SIGNAL_LEAK`~~ | — | Signals connected in `initGui()` but not disconnected in `unload()`. Surfaced via `qgis_context.signal_leaks` (informational; **not** emitted as an issue). | Ensure every `.connect()` in `initGui` has a matching `.disconnect()` in `unload`. |
| `UI_BLOCKING_LOOP` | 🔴 High | Intensive loops (getFeatures, sleep) in UI handlers without QgsTask. | Move heavy operations to a `QgsTask` to avoid freezing the interface. |
| `POTENTIAL_MISSING_SLOT` | 🟡 Medium | Signal connected to a method that doesn't exist in the class. | Verify the slot name exists and is correctly spelled in the target class. |

## 4. Security
| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `UNSAFE_SUBPROCESS` | 🔴 High | Use of `subprocess` with `shell=True` or variable interpolation in command strings. | Avoid `shell=True` and pass arguments as a list to prevent command injection. |
| `BLOCKING_NETWORK_CALL` | 🔴 High | Synchronous network calls (requests, urllib) in UI-related files. | Use `QgsTask` or `QNetworkAccessManager` to prevent freezing the QGIS interface. |

## 5. Resource Management
| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MANUAL_RESOURCE_PATH` | 🟡 Medium | Manual paths for icons or UI files (e.g., `icons/ico.png`). | Use the Qt resource system with the `:/plugins/...` prefix. |

## 6. Performance & Metrics
| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `SPATIAL_INDEX` | 🔴 High | Iteration over features using `getFeatures()` without a spatial index. | Use `QgsSpatialIndex` and `QgsFeatureRequest.setFilterRect()` to optimize spatial queries. |
| `HIGH_COMPLEXITY` | 🟡 Medium | Cyclomatic Complexity > 15 (includes 1.5x penalty for logic density). | Refactor complex functions by extracting sub-logics into smaller, testable methods. |

## 7. Architecture & Standards
| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `HEAVY_LOGIC_UI` | 🟡 Medium | Complex logic or heavy dependencies (pandas, numpy) detected in GUI files. | Move business logic and heavy imports to `core/` or service modules. |
| `QGIS_PROTECTED_MEMBER` | 🔴 High | Import of protected members (e.g., `qgis._core`). Unstable API. | Use the public API instead of internal members. |
| `IFACE_AS_ARGUMENT` | 🟡 Medium | Passing `QgisInterface` as an argument to functions. | Use the global `iface` or a Singleton pattern. |
| `GDAL_DIRECT_IMPORT` | 🟡 Medium | Direct `import gdal` instead of `from osgeo import gdal`. | Use `from osgeo import gdal` for consistency. |
| `QGIS_LEGACY_IMPORT` | 🔴 High | Direct import of `PyQt4` or `PyQt5`. | Use `qgis.PyQt` shim for maximum compatibility. |
| `MANDATORY_CLEANUP` | 🔴 High | `initGui()` implemented but `unload()` is missing. | Always implement `unload()` to prevent memory leaks and UI artifacts. |

## 7.1 Qt6 Migration (QGS4xx parity)

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `QT6_QAPP_USAGE` | 🟡 Medium | Use of `qApp`. | Use `QApplication.instance()`. |
| `QT6_QREGEXP_USAGE` | 🟡 Medium | Use of `QRegExp` (removed in Qt6). | Use `QRegularExpression`. |
| `QT6_QDESKTOPWIDGET` | 🟡 Medium | Use of `QDesktopWidget` (removed in Qt6). | Remove or use an alternative. |
| `QT6_REMOVED_ENUM` | 🟡 Medium | Use of a removed/renamed Qt6 enum (e.g. `Qt.MidButton`). | Use the new Qt6 enum. |
| `QT6_QFONTMETRICS_WIDTH` | 🟡 Medium | `QFontMetrics.width()` (removed in Qt6). | Use `QFontMetrics.horizontalAdvance()`. |
| `QT6_QCOMBOBOX_ACTIVATED` | 🟡 Medium | `QComboBox.activated[str]` (removed in Qt6). | Use `QComboBox.textActivated`. |
| `QT6_COMPILED_RESOURCES` | 🟡 Medium | Compiled resource imports (`*_rc`, removed in PyQt6). | Load resources by file path. |
| `QT6_ADDACTION_MULTIARG` | 🟡 Medium | `addAction(...)` with multiple arguments (removed in Qt6). | Create a `QAction` and call `addAction(action)`. |
| `QT6_QVARIANT_NULL` | 🟡 Medium | `QVariant()` / `QVariant(QVariant.Null)`. | Use `NULL`. |
| `QT6_QDATETIME_ARGS` | 🟡 Medium | Legacy `QDateTime(yyyy, mm, dd, hh, MM, ss, ms, ts)`. | Use `QDateTime(QDate(...), QTime(...))`. |
| `QT6_QDATETIME_QDATE` | 🟡 Medium | Legacy `QDateTime(QDate(...))`. | Use `QDateTime(QDate(...), QTime(0, 0, 0))`. |

## 8. General Python Best Practices
| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `PRINT_STATEMENT` | 🟢 Low | Use of `print()` statements in production code. | Use `QgsMessageLog` for user-facing logs or standard `logging` for debug. |

## 9. Design Patterns & Anti-patterns

Detected by `PatternsVisitor` (`src/analyzer/visitors/patterns_visitor.py`). All
are **informational** (`info`/Low) and suppressible with `# noqa`.

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `GOD_OBJECT` | 🟢 Low | Class with more than 20 methods or more than 15 instance attributes. | Split responsibilities into smaller, cohesive classes. |
| `SPAGHETTI_CODE` | 🟢 Low | Function with cyclomatic complexity > 20 or nesting depth > 4. | Extract sub-logic into smaller, testable functions. |
| `MAGIC_NUMBER` | 🟢 Low | Numeric literal (other than 0/1/-1/2) used in a comparison. | Extract into a named constant. |
| `DEAD_CODE` | 🟢 Low | Block/loop guarded by an always-false condition (`if False:` / `while 0:`). | Remove the unreachable code. |

### Informational (not issues)

| Name | Description |
| :--- | :--- |
| `patterns` (output field) | Design patterns detected per module: `singleton`, `factory`, `observer`, `strategy`, `decorator`. |
| `optimizations` (output field) | Generic suggestions: `module_too_large` (> 400 lines), `complexity_refactoring` (high-complexity module with many functions). |
| `halstead` (per-module metric) | Halstead `vocabulary`, `length`, `volume`, `difficulty`, `effort`. |
