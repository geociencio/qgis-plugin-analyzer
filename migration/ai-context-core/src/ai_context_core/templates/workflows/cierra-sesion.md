
---
description: Finaliza sesión: corre tests, actualiza logs (Dev/Maintenance), regenera contexto IA y propone commit de cierre.
---

Este workflow asegura un cierre limpio y documentado del trabajo realizado.

1.  **Sanity Check (Tests)**:
    Verifica que no rompimos nada crítico antes de irnos.
    ```bash
    uv run python -m unittest discover tests
    ```

2.  **Actualización de Memoria (Logs)**:
    *   Lee `docs/DEVELOPMENT_LOG.md`.
    *   Genera y escribe una nueva entrada con fecha de hoy (`## [YYYY-MM-DD] Resumen`) resumiendo los logros de esta sesión.
    *   Si hubo cambios estructurales, actualiza `docs/source/MAINTENANCE_LOG.md`.

3.  **Sincronización de Contexto Final**:
    Actualiza las métricas y la memoria de largo plazo del proyecto.
    // turbo
    ```bash
    ai-ctx analyze
    ```

4.  **Commit de Cierre (Propuesta)**:
    Revisa el estado y propone un commit.
    ```bash
    git status
    ```
    (El modelo propondrá `git add .` y `git commit` con un mensaje adecuado basado en el contexto. Espera confirmación).

5.  **Despedida**:
    Muestra un resumen final de lo logrado y cierra la sesión.
