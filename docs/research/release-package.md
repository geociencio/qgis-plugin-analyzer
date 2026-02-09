---
description: "Automatiza el proceso de release: validación de calidad, versionado, git tagging y build."
agent: QA Engineer
skills:
  - project-context
  - tech-stack
  - commit-standards
---

# Workflow: Liberar Versión (Release)

Este workflow asegura que cada versión pública de `qgis-plugin-analyzer` sea estable, esté documentada y sea trazable.

## 1. Auditoría de Calidad (Puerta de Enlace)

Antes de cualquier cambio de versión, el sistema debe ser auditado de forma profesional.

// turbo
```bash
# 1. Auditoría de estándares QGIS (Perfil Release)
uv run qgis-analyzer analyze . --profile release

# 2. Análisis estático y estilo
uv run ruff check .

# 3. Verificación de tipos estricta
uv run mypy . 

# 4. Tests unitarios
uv run pytest
```

> **STOP**: No procedas si hay errores en MyPy, fallos en Tests o si los scores de calidad son insuficientes.

## 2. Preparación del Release

1.  **Versionado**: Actualiza `version` en `pyproject.toml`.
2.  **Changelog**: Registra los cambios de la nueva versión en `CHANGELOG.md` siguiendo el formato "Keep a Changelog".
3.  **Release Notes**: Crea un documento en `docs/releases/notes/v[VERSION].md` con un **título descriptivo y profesional** (ej: `# v1.6.0: Official Repository Validation...`).
4.  **Sincronización de Docs**: Revisa que `README.md` y otros manuales estén al día.
5.  **Entorno**: Asegúrate de que `uv.lock` esté actualizado (`uv sync`).

## 3. Operaciones de Git

Estandariza los mensajes y etiquetas siguiendo Conventional Commits.

```bash
git add pyproject.toml CHANGELOG.md README.md docs/ uv.lock
git commit -m "chore(release): prepare v[VERSION]"
git tag -a "v[VERSION]" -m "Release v[VERSION] - [Título Descriptivo]"
git push origin main --tags
```

## 4. Construcción y Publicación

Genera los artefactos y prepara la release en GitHub.

// turbo
```bash
# Limpiar builds previos
rm -rf dist/

# Construir sdist y wheel
uv run python -m build

# Crear Release en GitHub (opcional si usas 'gh' cli)
gh release create "v[VERSION]" --title "v[VERSION] - [Título]" --notes-file docs/releases/notes/v[VERSION].md
gh release upload "v[VERSION]" dist/*
```

## Resultado Esperado
- Versión actualizada en `pyproject.toml`.
- Etiqueta de Git creada y subida al remoto.
- Notas de versión con títulos descriptivos.
- Artefactos de distribución generados correctamente en `dist/`.
