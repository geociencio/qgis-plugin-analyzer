# Reporte de Análisis y Sugerencias: Adaptación de .ai-context

Este documento detalla las discrepancias encontradas entre el sistema de contexto actual y la realidad del proyecto `qgis-plugin-analyzer`, junto con sugerencias prácticas para su adaptación.

## 🔍 Hallazgos Principales

Actualmente, el directorio `.ai-context` parece ser una copia o una herencia del proyecto **sec_interp** (un plugin de QGIS), lo que genera una desalineación crítica:

1.  **Identidad**: `project_brain.md` y `tech_stack.yaml` mencionan a "sec_interp".
2.  **Métricas**: Las métricas reportadas (15k+ líneas) no coinciden con las reales (~4.4k líneas).
3.  **Arquitectura**: Se mencionan patrones como MVC y Snapping manual que no aplican a esta herramienta CLI.
4.  **Calidad**: El score reportado era 92.0, pero el análisis real arroja **55.5**, principalmente por falsos negativos al tratar de validar el propio analizador como si fuera un plugin (ej. falta de `metadata.txt`).

---

## 💡 Sugerencias de Adaptación

### 1. Actualización de la Identidad (`project_brain.md`)
- **Nombre**: Cambiar de `sec_interp` a `qgis-plugin-analyzer`.
- **Visión**: Redefinir como "Motor de análisis estático y auto-fix para plugins de QGIS".
- **Componentes Críticos**: Reemplazar componentes de GUI por los núcleos de análisis:
    - `src/analyzer/engine.py` (Orquestador)
    - `src/analyzer/scanner.py` (Reglas AST)
    - `src/analyzer/fixer.py` (Lógica de transformación)

### 2. Refactorización del Stack Tecnológico (`tech_stack.yaml`)
- **Eliminar Dependencias de Runtime QGIS**: El analizador debe ser independiente. `PyQGIS` y `Qt5` deben marcarse como "Target" (objetivo de análisis), no como dependencias del proyecto.
- **Incluir Herramientas**: Reflejar el uso de `ruff` y la librería estándar (`ast`).

### 3. Ajuste de Scripts de Análisis
- **Configuración de `analyze_project_optfixed.py`**:
    - Ajustar para que ignore la validación de "Plugin QGIS" cuando se analiza a sí mismo.
    - Asegurar que la ruta base de búsqueda incluya `src/`.

### 4. Mejora de Reglas en `prompt_inicial.md`
- Mantener la regla de **Escapado de Metadatos** (%%) pero clasificarla como una "Restricción de Salida/Fix", no como una regla del código fuente del analizador.

### 5. Sincronización de Métricas
- Ejecutar el ciclo de sincronización para que `project_brain.md` refleje el Score de Calidad real (55.5) y las áreas de alta complejidad detectadas (`engine.py` con complejidad 62).

---

> [!IMPORTANT]
> No he realizado ningún cambio en los archivos existentes, este reporte es puramente informativo.
