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

2. **Sincronización de Versión & Docs**:
   - Actualizar `version` en `pyproject.toml`.
   - Actualizar `CHANGELOG.md`.
   - **Generar Release Notes**: Crear `docs/releases/notes/v[VERSION].md` con un título descriptivo y profesional (ej: `v[VERSION]: [Hito Principal] 🛡️`).
   - **Actualización de Documentos**: Asegurar que `README.md` y `RULES.md` reflejan los últimos cambios.
   - Sincronizar entorno: `uv sync`.

3. **Verificación Técnica**:
   // turbo
   ```bash
   uv run pytest && uv run mypy .
   ```

4. **Git Operations**:
   ```bash
   git add pyproject.toml CHANGELOG.md README.md docs/ uv.lock
   git commit -m "chore(release): prepare v[VERSION]"
   git tag -a "v[VERSION]" -m "Release v[VERSION] - [Hito Principal]"
   git push origin main --tags
   ```

5. **Build & Release**:
   // turbo
   ```bash
   rm -rf dist/
   uv run python -m build
   ```
   - Crear Release en GitHub usando `gh release create` vinculando las notas creadas.
