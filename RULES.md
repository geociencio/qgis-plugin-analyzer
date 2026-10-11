# Rule Catalog: QGIS Plugin Analyzer 📜

> **Generated** by `scripts/generate_rules_md.py` from
> `src/analyzer/rules/catalog.py` — do not edit by hand.

This document details the audit rules implemented in the analyzer to ensure that
plugins follow official QGIS standards and development best practices.

All rules support inline suppression via `# noqa` (suppress everything on the
line) or `# noqa: RULE_ID` (suppress a single rule).

The listed severity is the analyzer's default emitted severity; a profile
`[tool.qgis-analyzer.profiles.<p>.rules]` entry may override it per rule.

## 1. Internationalization (i18n)

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MISSING_I18N` | 🔴 High | Untranslated user-facing string literal (AST-based; excludes docstrings and technical strings). | Wrap strings in `self.tr("Text")` or `QCoreApplication.translate()`, or add `# no-i18n`. |

## 2. Obsolete API and Precision

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `OBSOLETE_API` | 🔴 High | Use of old methods like `writeAsVectorFormat()`. | Use the modern V3 version: `QgsVectorFileWriter.writeAsVectorFormatV3()`. |
| `OBSOLETE_VARIANT` | 🟡 Medium | Use of obsolete `QVariant` type constants (e.g., `QVariant.String`). | Use `QMetaType.Type.QString` or native types depending on the QGIS version. |
| `UNPRECISE_LAYER` | 🟡 Medium | Use of `mapLayersByName()`. | Use `mapLayers()` or unique layer IDs to avoid ambiguity with duplicate names. |

## 3. Threading Security & Safety

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `UI_BLOCKING_LOOP` | 🔴 High | Intensive loops (getFeatures, sleep) in UI handlers without QgsTask. | Move heavy operations to a `QgsTask` to avoid freezing the interface. |
| `UNSAFE_THREAD` | 🔴 High | Use of standard Python `threading.Thread`. | Use `QgsTask` or `QThread` to safely interact with the QGIS main thread. |
| `POTENTIAL_MISSING_SLOT` | 🟡 Medium | Signal connected to a method that doesn't exist in the class. | Verify the slot name exists and is correctly spelled in the target class. |
| ~~`SIGNAL_LEAK`~~ | — | Signals connected in `initGui()` but not disconnected in `unload()` (informational; surfaced via `qgis_context.signal_leaks`, **not** emitted as an issue). | Ensure every `.connect()` in `initGui` has a matching `.disconnect()` in `unload`. |

## 4. Security

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `AWS_KEY` | 🔴 High | Possible hardcoded AWS access key. | Rotate the key and load it from the environment. |
| `B102` | 🔴 High | Use of the builtin `exec()` (arbitrary code execution). | Avoid `exec()` on untrusted input. |
| `B301` | 🔴 High | Use of `pickle.load()` (insecure deserialization). | Avoid deserializing untrusted data; use a safe format such as JSON. |
| `B307` | 🔴 High | Use of the builtin `eval()` (arbitrary code execution). | Avoid `eval()` on untrusted input. |
| `B602` | 🔴 High | `subprocess` call with `shell=True`. | Pass arguments as a list and avoid `shell=True`. |
| `B608` | 🔴 High | Possible SQL injection via string formatting. | Use parameterized queries instead of string formatting. |
| `BLOCKING_NETWORK_CALL` | 🔴 High | Synchronous network calls (requests, urllib) in UI-related files. | Use `QgsTask` or `QNetworkAccessManager` to prevent freezing the QGIS interface. |
| `GOOGLE_API_KEY` | 🔴 High | Possible hardcoded Google API key. | Restrict/rotate the key and load it from the environment. |
| `TWILIO_KEY` | 🔴 High | Possible hardcoded Twilio key. | Rotate the key and load it from the environment. |
| `UNSAFE_SUBPROCESS` | 🔴 High | Use of `subprocess` with `shell=True` or variable interpolation in command strings. | Avoid `shell=True` and pass arguments as a list to prevent command injection. |
| `GENERIC_SECRET` | 🟡 Medium | Possible hardcoded secret assigned to a sensitive-looking name. | Load secrets from the environment or a secret manager. |
| `HARDCODED_SECRET` | 🟡 Medium | Possible hardcoded secret in an assignment (password/token/api_key/...). | Load secrets from environment variables or a secret manager. |
| `HIGH_ENTROPY` | 🟡 Medium | High-entropy string (possible token/key). | Verify it is not a secret; load secrets from the environment. |

## 5. Resource Management

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MANUAL_RESOURCE_PATH` | 🟡 Medium | Manual paths for icons or UI files (e.g., `icons/ico.png`). | Use the Qt resource system with the `:/plugins/...` prefix. |

## 6. Performance & Metrics

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `SPATIAL_INDEX` | 🔴 High | Iteration over features using `getFeatures()` without a spatial index/filter. | Use `QgsSpatialIndex` and `QgsFeatureRequest.setFilterRect()` to optimize spatial queries. |
| `HIGH_COMPLEXITY` | 🟡 Medium | Cyclomatic complexity > 15 (includes a logic-density penalty). | Refactor complex functions by extracting sub-logic into smaller, testable methods. |
| `NON_PYTHONIC_LOOP` | 🟢 Low | Manual index counter (`i += 1` used as a subscript) inside a loop. | Use `enumerate()` or iterate the collection directly. |

## 7. Architecture & Standards

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MANDATORY_CLEANUP` | 🔴 High | `initGui()` implemented but `unload()` is missing. | Always implement `unload()` to prevent memory leaks and UI artifacts. |
| `QGIS_LEGACY_IMPORT` | 🔴 High | Direct import of `PyQt4` or `PyQt5`. | Use the `qgis.PyQt` shim for maximum compatibility. |
| `QGIS_PROTECTED_MEMBER` | 🔴 High | Import of protected members (e.g., `qgis._core`). Unstable API. | Use the public API instead of internal members. |
| `GDAL_DIRECT_IMPORT` | 🟡 Medium | Direct `import gdal` instead of `from osgeo import gdal`. | Use `from osgeo import gdal` for consistency. |
| `HEAVY_LOGIC_UI` | 🟡 Medium | Complex logic or heavy dependencies (pandas, numpy) detected in GUI files. | Move business logic and heavy imports to `core/` or service modules. |
| `IFACE_AS_ARGUMENT` | 🟡 Medium | Passing `QgisInterface` as an argument to functions. | Use the global `iface` or a Singleton pattern. |
| `LEGACY_GDAL_IMPORT` | 🟡 Medium | Legacy `import gdal` detected (pre-osgeo style). | Use `from osgeo import gdal`. |
| `PYQT5_IMPORT` | 🟡 Medium | PyQt5 import detected. | Consider upgrading to PyQt6/PySide6. |
| `LEGACY_SIGNAL_SLOT` | 🟢 Low | Legacy `SIGNAL`/`SLOT` string marker detected. | Use the modern Python/`qgis.PyQt` signal-slot syntax. |

## 7.1. Qt6 Migration (QGS4xx parity)

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `QT6_ADDACTION_MULTIARG` | 🟡 Medium | `addAction(...)` with multiple arguments (removed in Qt6). | Create a `QAction` and call `addAction(action)`. |
| `QT6_COMPILED_RESOURCES` | 🟡 Medium | Compiled resource imports (`*_rc`, removed in PyQt6). | Load resources by file path. |
| `QT6_QAPP_USAGE` | 🟡 Medium | Use of `qApp`. | Use `QApplication.instance()`. |
| `QT6_QCOMBOBOX_ACTIVATED` | 🟡 Medium | `QComboBox.activated[str]` (removed in Qt6). | Use `QComboBox.textActivated`. |
| `QT6_QDATETIME_ARGS` | 🟡 Medium | Legacy `QDateTime(yyyy, mm, dd, hh, MM, ss, ms, ts)`. | Use `QDateTime(QDate(...), QTime(...))`. |
| `QT6_QDATETIME_QDATE` | 🟡 Medium | Legacy `QDateTime(QDate(...))`. | Use `QDateTime(QDate(...), QTime(0, 0, 0))`. |
| `QT6_QDESKTOPWIDGET` | 🟡 Medium | Use of `QDesktopWidget` (removed in Qt6). | Remove it or use an alternative. |
| `QT6_QFONTMETRICS_WIDTH` | 🟡 Medium | `QFontMetrics.width()` (removed in Qt6). | Use `QFontMetrics.horizontalAdvance()`. |
| `QT6_QREGEXP_USAGE` | 🟡 Medium | Use of `QRegExp` (removed in Qt6). | Use `QRegularExpression`. |
| `QT6_QVARIANT_NULL` | 🟡 Medium | `QVariant()` / `QVariant(QVariant.Null)`. | Use `NULL`. |
| `QT6_REMOVED_ENUM` | 🟡 Medium | Use of a removed/renamed Qt6 enum (e.g. `Qt.MidButton`). | Use the new Qt6 enum. |

## 8. General Python Best Practices

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MISSING_DOCSTRING` | 🟡 Medium | Public module, class or function without a docstring (PEP 257). | Add a Google-style docstring. |
| `MISSING_TYPE_HINTS` | 🟡 Medium | Function without type annotations. | Add type hints to the parameters and the return value. |
| `PRINT_STATEMENT` | 🟢 Low | Use of `print()` statements in production code. | Use `QgsMessageLog` for user-facing logs or standard `logging` for debug. |

## 9. Design Patterns & Anti-patterns

Detected by `PatternsVisitor` (`src/analyzer/visitors/patterns_visitor.py`). All are **informational** (`low`) and suppressible with `# noqa`.

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `DEAD_CODE` | 🟢 Low | Block/loop guarded by an always-false condition (`if False:` / `while 0:`). | Remove the unreachable code. |
| `GOD_OBJECT` | 🟢 Low | Class with more than 20 methods or more than 15 instance attributes. | Split responsibilities into smaller, cohesive classes. |
| `MAGIC_NUMBER` | 🟢 Low | Numeric literal (other than 0/1/-1/2) used in a comparison. | Extract it into a named constant. |
| `SPAGHETTI_CODE` | 🟢 Low | Function with cyclomatic complexity > 20 or nesting depth > 4. | Extract sub-logic into smaller, testable functions. |

### Informational (not issues)

| Name | Description |
| :--- | :--- |
| `patterns` (output field) | Design patterns detected per module: `singleton`, `factory`, `observer`, `strategy`, `decorator`. |
| `optimizations` (output field) | Generic suggestions: `module_too_large` (> 400 lines), `complexity_refactoring` (high-complexity module with many functions). |
| `halstead` (per-module metric) | Halstead `vocabulary`, `length`, `volume`, `difficulty`, `effort`. |

