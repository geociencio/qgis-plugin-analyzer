---
name: release-management
description: Estándares para el proceso de liberación del paquete Python qgis-plugin-analyzer.
trigger: al preparar lanzamientos, actualizar versiones o usar el workflow /release-plugin
---

# Gestión de Releases (Versión Package)

Controla el ciclo de vida de las versiones del paquete `qgis-plugin-analyzer`, garantizando calidad y consistencia en cada entrega a PyPI/GitHub.

## Cuándo usar este skill
- Al finalizar un sprint o corrección de bugs.
- Al actualizar `pyproject.toml` para una nueva versión.
- Al generar notas de versión o actualizar el changelog.
- Al usar el workflow `/release-plugin`.

## Grado de Libertad
- **Estricto**: El cumplimiento de Semantic Versioning y los checks de calidad es obligatorio.

## Workflow Detallado

### Fase 1: Calidad y Preparación
1. **Análisis de Calidad**:
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results --profile release
   ```
   - Validar: Score > Aceptable (definido en badges), cobertura de tests > 80%.
2. **Linting & Type Checking**:
   ```bash
   uv run ruff check .
   uv run mypy .
   ```

### Fase 2: Versionado
1. **Sincronización**: Actualizar `version` en `pyproject.toml`.
2. **Changelog**: Añadir entrada en `CHANGELOG.md` siguiendo el formato [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
3. **Reglas Semver**:
   - MAJOR (X): Cambios incompatibles en la API CLI/Librería.
   - MINOR (Y): Nuevas reglas de análisis o features.
   - PATCH (Z): Bug fixes.

### Fase 3: Verificación Técnica
1. **Tests Completos**:
   ```bash
   uv run pytest
   ```
   (Opcional: tests de integración con QGIS si aplica)

### Fase 4: Git y Etiquetado
1. Commit de release: `chore(release): prepare vX.Y.Z`.
2. Etiqueta: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
3. Push: `git push origin main --tags`.

### Fase 5: Empaquetado y Distribución
1. **Clean**: `rm -rf dist/ build/`
2. **Build**:
   ```bash
   uv run python -m build
   ```
3. **Validación**: Verificar contenido de `.tar.gz` y `.whl`.
4. **Release**: Crear release en GitHub adjuntando los artefactos. (La publicación a PyPI se suele manejar vía CI).

## Checklist de Calidad
- [ ] ¿El análisis estático pasa sin errores críticos?
- [ ] ¿La versión en `pyproject.toml` es correcta?
- [ ] ¿El `CHANGELOG.md` está actualizado?
- [ ] ¿Los tests pasan localmente?
