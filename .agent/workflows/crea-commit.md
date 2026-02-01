---
description: Crear commits limpios siguiendo Conventional Commits y validación de calidad.
agent: QA & Release Engineer
skills: [qa-docker, commit-standards]
validation:
  - Ruff y MyPy pasando
  - Mensaje sigue estándar
---

Este workflow asegura que cada commit aporte valor y mantenga la calidad.

1. **Linting Preliminar**:
   // turbo
   ```bash
   uv run ruff check --fix . && uv run ruff format .
   ```

2. **Stage**:
   ```bash
   git add .
   ```

3. **Validación de Calidad**:
   - Comprobar que no hay regresiones críticas.
   - Si es necesario, correr `uv run pytest`.

4. **Generación de Mensaje**:
   🤖 **Agent Action**: Usar **commit-standards** para proponer mensaje basado en `git diff --cached`.
   Formatos: `feat`, `fix`, `chore`, `refactor`, `docs`, `style`.

5. **Commit**:
   ```bash
   git commit -m "type(scope): description"
   ```
