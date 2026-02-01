---
description: Workflow guiado para refactorización segura.
agent: Static Analysis Architect
skills: [coding-standards, project-context]
validation:
  - CC < 15
  - Tests pasando
---

Guía la mejora del código sin alterar su comportamiento externo.

1. **Identificar Hotspots**:
   // turbo
   ```bash
   uv run qgis-analyzer analyze . --profile release
   ```

2. **Refactorizar**:
   🤖 **Agent Action**: Aplicar reducciones de complejidad, extracción de métodos y mejoras de tipado apoyándose en **coding-standards**.

3. **Validar Cambios**:
   // turbo
   ```bash
   uv run pytest && uv run mypy .
   ```

4. **Commit**:
   Usar `/crea-commit` con tipo `refactor`.
