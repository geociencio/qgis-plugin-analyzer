---
description: Proceso unificado de liberación del paquete Python.
agent: QA & Release Engineer
skills: [release-management, qa-docker, commit-standards]
validation:
  - Tests en verde
  - Versión correcta en pyproject.toml
  - Build generado sin errores
---

Flujo de liberación para `qgis-plugin-analyzer`.

1. **Preparación**:
   🤖 **Agent Action**: Usar **release-management** para validar estado previo.
   // turbo
   ```bash
   uv run qgis-analyzer analyze . --profile release
   ```

2. **Sincronización de Versión**:
   - Actualizar `pyproject.toml`.
   - Actualizar `CHANGELOG.md`.

3. **Verificación Técnica**:
   // turbo
   ```bash
   uv run pytest && uv run mypy .
   ```

4. **Git Operations**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore(release): prepare vX.Y.Z"
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin main --tags
   ```

5. **Build & Release**:
   // turbo
   ```bash
   rm -rf dist/
   uv run python -m build
   ```
   - Crear Release en GitHub.
