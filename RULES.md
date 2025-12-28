# Catálogo de Reglas: QGIS Plugin Analyzer 📜

Este documento detalla las reglas de auditoría automática implementadas en el analizador para garantizar que los plugins sigan los estándares oficiales de QGIS y las mejores prácticas de desarrollo.

## 1. Internacionalización (i18n)

| ID de Regla | Severidad | Descripción | Recomendación |
| :--- | :--- | :--- | :--- |
| `MISSING_I18N` | 🔴 Alta | Detecta cadenas de texto en la interfaz (setText, setToolTip, etc.) que no están envueltas en funciones de traducción. | Envolver las cadenas en `self.tr("Texto")` o `QCoreApplication.translate()`. |

## 2. API Obsoleta y Precisión

| ID de Regla | Severidad | Descripción | Recomendación |
| :--- | :--- | :--- | :--- |
| `OBSOLETE_API` | 🔴 Alta | Uso de métodos antiguos como `writeAsVectorFormat()`. | Usar la versión moderna V3: `QgsVectorFileWriter.writeAsVectorFormatV3()`. |
| `OBSOLETE_VARIANT`| 🟡 Media | Uso de constantes de tipo obsoletas de `QVariant` (ej. `QVariant.String`). | Usar `QMetaType.Type.QString` o tipos nativos según la versión de QGIS. |
| `UNPRECISE_LAYER` | 🟡 Media | Uso de `mapLayersByName()`. | Usar `mapLayers()` o IDs únicos de capa para evitar ambigüedad con nombres duplicados. |

## 3. Seguridad en Hilos (Threading)

| ID de Regla | Severidad | Descripción | Recomendación |
| :--- | :--- | :--- | :--- |
| `UNSAFE_THREAD` | 🔴 Alta | Uso de `threading.Thread` estándar de Python. | Usar `QgsTask` o `QThread` para interactuar de forma segura con el hilo principal de QGIS. |

## 4. Gestión de Recursos

| ID de Regla | Severidad | Descripción | Recomendación |
| :--- | :--- | :--- | :--- |
| `MANUAL_PATH` | 🟡 Media | Rutas manuales para iconos o archivos UI (ej. `icons/ico.png`). | Usar el sistema de recursos de Qt con el prefijo `:/plugins/...`. |

## 5. Rendimiento (Performance)

| ID de Regla | Severidad | Descripción | Recomendación |
| :--- | :--- | :--- | :--- |
| `SPATIAL_INDEX` | 🔴 Alta | Iteración sobre entidades sin usar un índice espacial en capas pesadas. | Utilizar `QgsSpatialIndex` para optimizar las consultas espaciales. |

## 6. Arquitectura

| ID de Regla | Severidad | Descripción | Recomendación |
| :--- | :--- | :--- | :--- |
| `HEAVY_LOGIC_UI` | 🟡 Media | Lógica compleja o dependencias pesadas detectadas dentro de archivos de la interfaz gráfica (GUI). | Mover la lógica de negocio a `core/services/` o `core/logic/`. |
