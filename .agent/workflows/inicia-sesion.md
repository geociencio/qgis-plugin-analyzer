---
description: Inicializa la sesión con contexto y entorno sincronizado.
agent: Static Analysis Architect
skills: [project-context]
validation:
  - Tests corriendo
  - Entorno uv sincronizado
  - Contexto cargado
---

Este workflow prepara el entorno para una sesión productiva.

1. **Sincronización de Entorno**:
   Asegura que las dependencias estén al día.
   // turbo
   ```bash
   uv sync
   ```

2. **Actualización de Contexto**:
   Ejecuta el analizador de contexto para tener la última foto del proyecto.
   // turbo
   ```bash
   uv run ai-ctx analyze
   ```

3. **Sanity Check**:
   Verifica el estado actual de los tests usando `unittest`.
   ```bash
   uv run python -m unittest discover tests
   ```

4. **Revisión de Tareas**:
   Lee `task.md` y `.agent/next_steps.md` para recordar dónde nos quedamos.
