---
description: "Finaliza sesión: corre tests, actualiza logs y propone commit."
agent: Static Analysis Architect
skills: [project-context, qa-docker]
validation:
  - Tests pasando (GREEN)
  - Logs actualizados
---

Este workflow asegura un cierre limpio.

1. **Sanity Check Final**:
   // turbo
   ```bash
   uv run pytest
   ```

2. **Actualización de Memoria**:
   - Actualizar `docs/DEVELOPMENT_LOG.md` con el resumen del día.
   - Reflejar métricas finales con `uv run ai-ctx analyze .`.

3. **Limpieza**:
   - Borrar archivos temporales o artefactos de debug.

4. **Propuesta de Cierre**:
   Si hay cambios pendientes, sugerir usar el workflow `/crea-commit`.
