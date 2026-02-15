# Walkthrough: Refinamiento de Detección i18n

Se han implementado mejoras significativas en `StandardsVisitor` para reducir los falsos positivos en la detección de cadenas faltantes de traducción (`MISSING_I18N`), especialmente enfocadas en plugins de QGIS.

## Cambios Realizados

### 1. Heurística Inteligente en `is_translatable_string`
- **Exclusión por longitud**: Las cadenas de 5 caracteres o menos sin espacios son ignoradas (ej. "id", "data", "type").
- **Lista de palabras técnicas**: Se añadió una lista de términos comunes que no deben traducirse (whitelist).
- **Consistencia**: Se mantuvo la exclusión previa de `snake_case`, `CamelCase` y rutas.

### 2. Contexto de Detección en `visit_Constant`
- **Exclusión de Diccionarios**: Ahora se ignoran tanto las **claves** como los **valores** de los diccionarios, ya que suelen representar configuraciones o datos internos.
- **Funciones Ignoradas**: Se amplió `IGNORED_I18N_FUNCTIONS` con métodos comunes como `get`, `post`, `format`, `join`, `split`, evitando que las cadenas usadas en estos contextos sean marcadas.

### 3. Eliminación de Versión Hardcodeada
- **Implementación**: Se reemplazó la constante hardcodeada en `src/analyzer/__init__.py` por una consulta dinámica a `importlib.metadata`.
- **Beneficio**: Ahora la versión solo se define en el `pyproject.toml`, evitando inconsistencias.

## Verificación

### Tests Automatizados
...
```bash
uv run qgis-analyzer --version
# Output: qgis-analyzer 1.8.0b1
```
Se creó una nueva suite de pruebas específica: [test_i18n_heuristics.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-analyzer/qgis_plugin_analyzer/tests/test_i18n_heuristics.py).
- **Resultados**: 4 tests específicos exitosos.
- **Suite Completa**: 44 tests pasados con éxito.

### Análisis del Proyecto
Se ejecutó el analizador sobre el directorio `src/`:
- Se confirmó que cadenas como `"MISSING_I18N"` o `"high"` (usadas internamente en el código) ya no generan alertas, mientras que los mensajes de error legibles por el usuario siguen siendo detectados.

```bash
uv run qgis-analyzer analyze src/
# 44 tests PASSED
# 0 falsos positivos en claves de diccionarios y funciones técnicas.
```

## Implementación de Subcomandos en `analyze`

Se ha extendido el comando `analyze` para soportar análisis especializados mediante subcomandos, manteniendo 100% de compatibilidad con la sintaxis legacy.

### Subcomandos Disponibles

- **`analyze i18n [path]`**: Auditoría de internacionalización y traducciones
- **`analyze security [path]`**: Escaneo enfocado en vulnerabilidades de seguridad
- **`analyze performance [path]`**: Análisis de rendimiento y bloqueos de UI
- **`analyze architecture [path]`**: Análisis de dependencias y acoplamiento
- **`analyze metadata [path]`**: Validación de metadatos y estructura QGIS
- **`analyze all [path]`** o **`analyze [path]`**: Análisis completo (comportamiento por defecto)

### Arquitectura de la Implementación

1. **CLI (`src/analyzer/cli/commands/analyze.py`)**:
   - Despacho manual de argumentos para mantener compatibilidad legacy
   - Detección inteligente: `analyze i18n .` vs `analyze .`

2. **Motor (`src/analyzer/engine.py`)**:
   - Parámetro `scope` en `ProjectAnalyzer.run()`
   - Método `_filter_issues_by_scope()` para filtrar issues antes de guardar

3. **Visitors (`src/analyzer/visitors/`)**:
   - Parámetro `scope` propagado a todos los visitors
   - Filtrado en `BaseVisitor._should_report()` basado en scope
   - `CompositeVisitor` activa solo los visitors relevantes

4. **Worker Context (`src/analyzer/scanner.py`)**:
   - El scope se pasa a través del contexto compartido a los workers paralelos

### Verificación

```bash
# Análisis especializado en i18n
uv run qgis-analyzer analyze i18n .
# Output: ⚠️ Issue Statistics (1150 total) - MISSING_I18N: 1150

# Análisis completo (legacy compatible)
uv run qgis-analyzer analyze .
# Output: ⚠️ Issue Statistics (1266 total) - MISSING_I18N: 1150, MISSING_DOCSTRING: 86, ...
```

---

## Release v1.9.0: Specialized Analysis Subcommands 🎯

Se completó exitosamente el release de la versión 1.9.0, introduciendo subcomandos especializados para análisis dirigido.

### Subcomandos Implementados

- `analyze i18n [path]` - Auditoría de internacionalización (1,150 issues detectados)
- `analyze security [path]` - Escaneo de vulnerabilidades
- `analyze performance [path]` - Análisis de rendimiento
- `analyze architecture [path]` - Análisis de dependencias
- `analyze metadata [path]` - Validación de metadatos QGIS
- `analyze [path]` - Análisis completo (1,266 issues, legacy compatible)

### Proceso de Release

- ✅ Versión 1.9.0 publicada
- ✅ Tests: 49/49 passed
- ✅ Paquetes: tar.gz (92K) + wheel (98K)
- ✅ GitHub Release: [v1.9.0](https://github.com/geociencio/qgis-plugin-analyzer/releases/tag/v1.9.0)
- ✅ Roadmap CLI documentado: 3 fases de implementación futura
