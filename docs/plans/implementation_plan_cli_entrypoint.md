# Plan de Implementación: Entry Point CLI Único

> **Estado**: ✅ implementado (v1.19.3, 2026-11-05).
> **Meta**: dejar un solo entry point canónico (`analyzer.main:main`), eliminar la
> duplicación en `analyzer.cli` y soportar `python -m analyzer` sin introducir
> nuevas rutas de ejecución.
> **Origen**: revisión de `src/analyzer/cli/__init__.py` (2026-11-05).
> **Implementación**: `analyzer.cli` es re-export puro; `src/analyzer/__main__.py`
> añadido; 318 tests; entry point de `pyproject.toml` sin cambios.

## Diagnóstico

Estado actual:

```toml
# pyproject.toml
[project.scripts]
qgis-analyzer = "analyzer.main:main"
```

```text
qgis-analyzer
  → analyzer.main:main()          # función canónica
  → CLIApp()
  → CLIApp.run()
```

Pero existen dos implementaciones idénticas de `main()`:

- [src/analyzer/main.py](../../src/analyzer/main.py): usada por el console script.
- [src/analyzer/cli/__init__.py](../../src/analyzer/cli/__init__.py): define
  `main()` y lo exporta en `__all__`, pero **nadie lo usa**.

Además:

- No existe `src/analyzer/__main__.py`, por lo que `python -m analyzer` falla.
- `python -m analyzer.main` sí funciona.
- `analyzer.cli.main` es un símbolo público solo por el `__all__`; no tiene
  consumidores internos (`grep` en `src/`, `tests/` y `docs/`).

## Decisiones propuestas

1. **Un único `main` canónico** en `analyzer.main`.
2. `analyzer.cli.__init__` queda como re-export puro de `CLIApp`; sin `sys`,
   sin `main`, sin lógica de ejecución.
3. Añadir `src/analyzer/__main__.py` para que `python -m analyzer` invoque el
   mismo `main`.
4. **No** añadir `analyzer/cli/__main__.py`: `python -m analyzer.cli` seguirá
   sin ser una interfaz soportada.
5. Mantener `pyproject.toml` sin cambios: el entry point instalado sigue siendo
   `analyzer.main:main`.

### Compatibilidad de `analyzer.cli.main`

Es la única decisión con impacto potencial. Hay dos opciones:

| Opción | Ventaja | Coste |
|---|---|---|
| **A. Eliminarlo** (recomendada) | Una sola implementación; sin riesgo de divergencia | `from analyzer.cli import main` deja de funcionar |
| **B. Dejarlo como wrapper deprecado** | Conserva el import | Sigue existiendo una API duplicada y necesita una release de limpieza posterior |

**Recomendación**: opción A. No hay consumidores en el repositorio, no está
documentado como API pública y su comportamiento es idéntico al entry point
real. Si se quiere ser estricto con SemVer, aplicarla en una **minor** y anotar
la retirada; si se considera limpieza interna, una **patch** es suficiente.
Propuesta inicial: **v1.19.3 (patch)**, con nota en CHANGELOG.

## Cambios por archivo

### 1. `src/analyzer/cli/__init__.py`

Antes:

```python
"""CLI package for QGIS Plugin Analyzer."""

import sys

from .app import CLIApp


def main() -> None:
    """Main entry point for the QGIS Plugin Analyzer CLI."""
    app = CLIApp()
    sys.exit(app.run())


__all__ = ["CLIApp", "main"]
```

Después:

```python
"""CLI package for QGIS Plugin Analyzer."""

from .app import CLIApp

__all__ = ["CLIApp"]
```

### 2. `src/analyzer/__main__.py` (nuevo)

```python
"""Support ``python -m analyzer``."""

from .main import main

if __name__ == "__main__":
    main()
```

Notas:

- `main()` ya hace `sys.exit(app.run())`; no duplicar el exit.
- El guard `if __name__ == "__main__"` es el patrón estándar de `__main__.py`.
- `python -m analyzer.main` sigue funcionando sin cambios.

### 3. `src/analyzer/main.py`

Sin cambios funcionales. Se mantiene:

```python
from .cli import CLIApp


def main() -> None:
    """Main entry point for the QGIS Plugin Analyzer CLI."""
    app = CLIApp()
    sys.exit(app.run())
```

El import `.cli` sigue ejecutando el `__init__`, pero ahora solo re-exporta la
clase; no hay efecto secundario adicional.

## Tests

Nuevo `tests/test_cli_entrypoints.py`:

1. `test_cli_package_reexports_cli_app`
   - `from analyzer.cli import CLIApp` y `from analyzer.cli.app import CLIApp`
     devuelven la **misma** clase.

2. `test_cli_package_has_no_duplicate_main`
   - `import analyzer.cli as cli`
   - `assert not hasattr(cli, "main")` (solo si se elige opción A).

3. `test_python_m_analyzer_version`
   - `subprocess.run([sys.executable, "-m", "analyzer", "--version"], ...)`
   - `returncode == 0`, salida contiene la versión del paquete.

4. `test_python_m_analyzer_help`
   - `python -m analyzer` sin argumentos → `returncode == 0`,
     salida contiene `usage:` / comandos.

5. `test_console_script_entrypoint_is_canonical`
   - Leer `pyproject.toml` o `importlib.metadata.entry_points()` y afirmar
     `qgis-analyzer == "analyzer.main:main"`.
   - Evita que una futura edición vuelva a apuntar a `analyzer.cli:main`.

Los tests 3 y 4 usan `sys.executable` y el paquete editable del entorno de
pruebas; no requieren instalar el wheel. El test 5 protege el contrato de
empaquetado.

## Documentación

- `README.md`: añadir `python -m analyzer --version` junto a
  `qgis-analyzer --version`; aclarar que el entry point instalado no cambia.
- `CHANGELOG.md`: sección `Changed`/`Removed`:
  - “Eliminado `analyzer.cli.main` duplicado; `analyzer.main:main` es el único
    entry point.”
  - “Añadido `python -m analyzer`.”
- `docs/DEVELOPMENT_LOG.md` y notas de release si se publica.
- No tocar `RULES.md` (no hay reglas nuevas).

## Secuencia de implementación

1. Crear `tests/test_cli_entrypoints.py` con los cinco casos (algunos fallarán
   inicialmente).
2. Limpiar `src/analyzer/cli/__init__.py`.
3. Añadir `src/analyzer/__main__.py`.
4. Ejecutar:
   - `uv run pytest tests/test_cli_entrypoints.py tests/test_cli.py tests/test_cli_json.py -q`
   - `uv run ruff check .`
   - `uv run ruff format .`
   - `uv run mypy src/`
   - `uv run pytest tests/ -q`
   - `uv run qgis-analyzer analyze . --max-cc 15`
5. Verificar empaquetado:
   - `uv build`
   - `uvx twine check dist/*`
   - instalar wheel/sdist en venv limpio y comprobar `qgis-analyzer --version`.
6. Actualizar README/CHANGELOG y, si se publica, release **v1.19.3**.

## Criterios de aceptación

- [x] Existe una sola implementación de `main` en `src/analyzer/main.py`.
- [x] `analyzer.cli.__init__` solo re-exporta `CLIApp`.
- [x] `qgis-analyzer --version` funciona igual que antes.
- [x] `python -m analyzer --version` funciona.
- [x] `python -m analyzer.main --version` sigue funcionando.
- [x] `analyzer.cli.CLIApp` sigue importable.
- [x] Tests, ruff, mypy, self-analysis y `--profile release --strict` en verde.
- [x] Wheel/sdist conservan el boundary (`top_level = analyzer`).

## No objetivos

- No cambiar el parser, comandos ni el comportamiento de `CLIApp.run()`.
- No añadir `analyzer/cli/__main__.py`.
- No convertir `analyzer.cli` en una segunda interfaz de ejecución.
- No cambiar el nombre del console script ni el entry point de `pyproject.toml`.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Import circular si `cli` intenta importar `analyzer.main` | No importar `main` desde `cli`; solo `CLIApp` desde `.app` |
| Romper `from analyzer.cli import main` | Opción A documentada; opción B con wrapper deprecado si se exige compatibilidad |
| `python -m analyzer` no encuentra el paquete | Probar con el entorno editable y, además, con wheel instalado |
| Divergencia futura de entry points | Test 5 sobre `pyproject.toml`/metadata |
| Cambio de cobertura por código eliminado | No debe bajar del 80 %; cobertura actual ~89.5 % |
