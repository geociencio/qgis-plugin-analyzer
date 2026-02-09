# Rule Catalog: QGIS Plugin Analyzer 📜

This document details the automatic audit rules implemented in the analyzer to ensure that plugins follow official QGIS standards and development best practices.

## 1. Internationalization (i18n)

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MISSING_I18N` | 🔴 High | Detects text strings in the interface (setText, setToolTip, etc.) that are not wrapped in translation functions. | Wrap strings in `self.tr("Text")` or `QCoreApplication.translate()`. |

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
| `SIGNAL_LEAK` | 🔴 High | Signals connected in `initGui()` are not disconnected in `unload()`. | Ensure every `.connect()` in `initGui` has a corresponding `.disconnect()` in `unload` to prevent crashes. |
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

## 8. General Python Best Practices
| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `PRINT_STATEMENT` | 🟢 Low | Use of `print()` statements in production code. | Use `QgsMessageLog` for user-facing logs or standard `logging` for debug. |
