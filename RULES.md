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

## 3. Threading Security

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `UNSAFE_THREAD` | 🔴 High | Use of standard Python `threading.Thread`. | Use `QgsTask` or `QThread` to safely interact with the QGIS main thread. |

## 4. Resource Management

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `MANUAL_PATH` | 🟡 Medium | Manual paths for icons or UI files (e.g., `icons/ico.png`). | Use the Qt resource system with the `:/plugins/...` prefix. |

## 5. Performance

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `SPATIAL_INDEX` | 🔴 High | Iteration over features without using a spatial index on heavy layers. | Use `QgsSpatialIndex` to optimize spatial queries. |

## 6. Architecture

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `HEAVY_LOGIC_UI` | 🟡 Medium | Complex logic or heavy dependencies detected within graphical interface (GUI) files. | Move business logic to `core/services/` or `core/logic/`. |

## 7. QGIS Specific Standards (flake8-qgis inspired)

| Rule ID | Severity | Description | Recommendation |
| :--- | :--- | :--- | :--- |
| `QGIS_PROTECTED_MEMBER` | 🔴 High | Import of protected members (e.g., `qgis._core`). Unstable API. | Use the public API instead of internal members. |
| `IFACE_AS_ARGUMENT` | 🟡 Medium | Passing `QgisInterface` as an argument to functions. | Use the global `iface` or a Singleton pattern. |
| `GDAL_DIRECT_IMPORT` | 🟡 Medium | Direct `import gdal` instead of `from osgeo import gdal`. | Use `from osgeo import gdal` for consistency. |
| `QGIS_LEGACY_IMPORT` | 🔴 High | Direct import of `PyQt4` or `PyQt5`. | Use `qgis.PyQt` shim for maximum compatibility. |
| `MANDATORY_CLEANUP` | 🔴 High | `initGui()` implemented but `unload()` is missing. | Always implement `unload()` to prevent memory leaks and UI artifacts. |
