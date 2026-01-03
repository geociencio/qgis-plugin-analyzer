
📋 QGIS Audit Rules Catalog:
==============================
- [MEDIUM] UNPRECISE_LAYER: mapLayersByName() can be imprecise. Consider mapLayers() or unique IDs.
- [HIGH] UNSAFE_THREAD: threading.Thread usage detected. Prefer QgsTask or QThread.
- [MEDIUM] MANUAL_RESOURCE_PATH: Manual resource path detected. Use :/plugins/...
- [LOW] PRINT_STATEMENT: print() usage detected. Use QgsMessageLog.
- [MEDIUM] OBSOLETE_VARIANT: Obsolete QVariant type constants detected. Use QMetaType or native types.
- [HIGH] UNSAFE_SUBPROCESS: Potential unsafe subprocess usage. Avoid shell=True and ensure arguments are properly quoted.
- [HIGH] BLOCKING_NETWORK_CALL: Synchronous network call detected. UI blocking risk. Use QgsTask or QNetworkAccessManager.

Total: 7 rules.

