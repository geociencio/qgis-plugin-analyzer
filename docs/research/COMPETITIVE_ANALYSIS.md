# Competitive Analysis: QGIS Plugin Tools 🛡️

> **Última actualización**: 2026-09-14 (datos verificados en PyPI/GitHub).

## 1. Panorama del ecosistema

Las herramientas que compiten o se solapan se agrupan en cuatro categorías:

| Categoría | Herramientas |
| :--- | :--- |
| Linters QGIS específicos | `flake8-qgis` (OSGeo Suomi) |
| Empaquetado/release QGIS | `qgis-plugin-ci` (QGIS org), `qgis-plugin-repo` (3liz) |
| Linters/analizadores Python genéricos | `ruff`, `pylint`, `flake8`, `prospector`, `bandit`, `mypy`/`pyright`, `SonarQube` |
| Soporte/testing QGIS | `pytest-qgis`, `qgis_plugin_tools` (OSGeo Suomi) |

## 2. Competidor directo: `flake8-qgis`

**Estado (PyPI, mayo 2026)**: v2.1.0, MIT, `requires-python >=3.10`, mantenido por
OSGeo Suomi, publicado con Trusted Publishing (OIDC). Repositorio:
`osgeosuomi/flake8-qgis`.

Cubre **~25 reglas** (`QGS101`–`QGS111`, `QGS201`–`QGS202`, `QGS401`–`QGS412`):

- **Import hygiene**: `QGS101/102` (miembros protegidos `qgis._core`),
  `QGS103/104` (PyQt directo), `QGS106` (gdal directo), `QGS111` (processing directo).
- **API PyQGIS**: `QGS108/109` (`TEMPORARY_OUTPUT`), `QGS110`
  (`is_child_algorithm`), `QGS201/202` (valores de retorno).
- **Migración Qt6** (novedad de v2.x): `QGS401` (`qApp`), `QGS402` (`QVariant`),
  `QGS403` (enums), `QGS404`–`QGS412` (`QFontMetrics.width()`, `QRegExp`,
  `QDesktopWidget`, `QDateTime`, etc.).

**Fortalezas**: precisión en la API PyQGIS/Qt6, reglas accionables, mantenimiento activo.
**Debilidades**: solo lint (sin scores, i18n, seguridad, arquitectura, reports ni
auto-fix); monohilo (lento frente a Ruff).

## 3. Competidor de proceso: `qgis-plugin-ci`

**Estado**: `qgis/qgis-plugin-ci`, GPL-3.0, 69 ⭐, 777 commits.

Cubre: empaquetado `.zip`, release al repositorio oficial de QGIS, GitHub releases /
custom repo, gestión de traducciones con Transifex, compilación de `.qrc`, flag
`experimental`, changelog.

**No compite en calidad de código** — es complementario (release/translation).
Candidato ideal para integración CI conjunta.

## 4. Herramientas Python genéricas

| Herramienta | Foco | Notas 2026 |
| :--- | :--- | :--- |
| **Ruff** | Lint + format | 900+ reglas, Rust, 10-100× más rápido, drop-in de flake8/black/isort. Ya integrado. |
| **Bandit** | Seguridad | 8.3k ⭐, AST, reglas B1xx–B7xx. Reglas derivadas ya implementadas internamente. |
| **Pylint** | Lint comprehensivo | Potente pero lento/verboso; requiere mucha config. |
| **Mypy / Pyright** | Type checking | Estándar de typing; el analyzer solo mide cobertura, no hace checking real. |
| **Prospector** | Meta-linter | Envuelve pylint+pep8+mccabe; sin integración QGIS. |
| **SonarQube** | Plataforma | Comercial, quality gates corporativos; sin dominio QGIS. |

## 5. Tabla comparativa consolidada

| Capacidad | **qgis-plugin-analyzer** | flake8-qgis | qgis-plugin-ci | Ruff/Bandit |
| :--- | :---: | :---: | :---: | :---: |
| Reglas PyQGIS/Qt6 | ✅ (parcial Qt6) | ✅✅ (muy completo) | ❌ | ❌ |
| i18n por AST (`tr`/`translate`) | ✅ (maduro) | ❌ | ❌ | ❌ |
| Gate complejidad (`--max-cc`) | ✅ | ❌ | ❌ | ❌ (mccabe aparte) |
| Seguridad (secrets, subprocess) | ✅ | ❌ | ❌ | ✅ (Bandit) |
| Scores (quality/maintainability/security) | ✅ | ❌ | ❌ | ❌ |
| Arquitectura (deps, ciclos, coupling) | ✅ | ❌ | ❌ | ❌ |
| Auto-fix | ✅ | ❌ | ❌ | ✅ (Ruff --fix) |
| Reports (HTML/MD/JSON) | ✅ | ❌ | ❌ | parcial |
| Contrato CI (`--json` + schema) | ✅ | ❌ | ❌ | parcial |
| Release/Transifex | ❌ | ❌ | ✅✅ | ❌ |
| Empaquetado `.zip` plugin | ❌ | ❌ | ✅ | ❌ |
| Rendimiento | 🚀 (paralelo + Ruff) | 🐢 (flake8) | n/a | 🚀 |
| Runtime deps | solo stdlib + Ruff | flake8+plugins | múltiples | n/a |

## 6. Diagnóstico y posicionamiento

`qgis-plugin-analyzer` es el único que unifica calidad genérica (Ruff) + reglas
PyQGIS + i18n + seguridad + arquitectura + scoring + reports + auto-fix, con cero
dependencias de runtime y un contrato de salida para CI.

**Ventaja diferencial real** (post-Fases 0–5): la regla i18n AST y el gate
`--max-cc` no existen en ninguna otra herramienta. El sistema de *scoring* tampoco.

**Brechas concretas**:

1. **Paridad Qt6 incompleta**: flake8-qgis v2.x añadió 12 reglas `QGS4xx` de
   migración Qt6 (enums removidos, `QRegExp`, `QDesktopWidget`, `QDateTime`,
   `QFontMetrics.width`…). El analyzer cubre `PYQT5_IMPORT`/`QGIS_LEGACY_IMPORT`
   pero no esos *API removals* específicos.
2. **Type checking**: reporta cobertura de hints al 0% (bug del metrics visitor)
   y no hace checking real; mypy/pyright lo superan.
3. **Integración release**: no hace Transifex/empaquetado (qgis-plugin-ci);
   complementarios, no duplicar.

## 7. Recomendaciones priorizadas

1. **Cerrar paridad con `QGS4xx`** (migración Qt6) para poder reemplazar
   flake8-qgis por completo.
2. **Fix del type-hint coverage** (0% es incorrecto — regresión conocida).
3. **`ci-wizard`**: generar un workflow que corra `qgis-plugin-analyzer` (calidad)
   + `qgis-plugin-ci` (release) juntos.
4. **Trusted Publishers (OIDC)**: flake8-qgis ya publica con OIDC; el
   `release.yml` actual usa `PYPI_TOKEN`.
5. **Golden SecInterp**: ejecutar la validación golden para confirmar 0 FP y
   marcar la paridad i18n.

---

*Referencias: PyPI `flake8-qgis` 2.1.0 (2026-05-21), GitHub `qgis/qgis-plugin-ci`,
`PyCQA/bandit`, `astral-sh/ruff` docs.*
