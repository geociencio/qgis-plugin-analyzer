---
description: Inicializa la sesión: actualiza métricas, carga contexto crítico y verifica entorno.
---

Este workflow prepara el entorno para una sesión de desarrollo productiva.

1.  **Sintonización de Contexto**:
    Ejecuta el análisis del proyecto y **lee** los archivos de memoria resultantes para entender el estado actual.
    // turbo
    ```bash
    python3 .ai-context/analyze_project_optfixed.py
    ```
    
    Lee los siguientes archivos para cargar el contexto en memoria:
    *   `.ai-context/project_brain.md`
    *   `AI_CONTEXT.md`
    *   `docs/DEVELOPMENT_LOG.md`
    *   `task.md`

2.  **Sincronización de Entorno**:
    Asegura que las dependencias estén sincronizadas.
    // turbo
    ```bash
    uv sync
    ```

3.  **Sanity Check (Tests)**:
    Verifica que el código base esté estable antes de empezar a trabajar.
    ```bash
    uv run python -m unittest discover tests
    ```
