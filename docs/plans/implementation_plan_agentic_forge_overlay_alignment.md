# Plan de Implementación: Alineación del Overlay Agentic-Forge con ai-context-core

> **Estado**: propuesto — pendiente de aprobación del USER antes de implementar.
> **Meta**: subir el overlay de `qgis-plugin-analyzer` al nivel de madurez que
> `ai-context-core` alcanzó en v5.1.0 (2026-10-10), sin tocar el núcleo genérico
> del framework (`agentic-forge` `v1.2.0`).
> **Contexto**: `qgis-plugin-analyzer` ya adoptó `agentic-forge` (fue el **piloto**,
> 2026-10-08: `4b10b11` + `fb080db`). Base en su sitio: submódulo `.agent/`
> (`2de22cf` = `v1.2.0`), `forge.toml`, `.agent-state/`, `opencode.json`
> (3 subagentes allow/ask/deny) y `AGENTS.md` canónico. Lo que falta es el
> **overlay de proyecto**, donde ai-context-core está por delante.

## 0. Evidencia

- `git submodule status` → `.agent 2de22cf... (v1.2.0)` (mismo pin que ai-context-core).
- `python .agent/tools/forge.py validate` → **11 skills (9 framework + 2 overlay), 14 workflows**, OK.
- Overlay actual: `.agent-state/skills/{domain-logic,project-context}` (2).
- Overlay de ai-context-core: `{domain-logic, project-context, tech-stack, debug-specialist, skill-authoring, release-ai-context-core}` (6).

## 1. Análisis de brecha

| Elemento | ai-context-core | qgis-plugin-analyzer | Acción |
| :--- | :--- | :--- | :--- |
| Base (submódulo/forge.toml/state/opencode.json) | ✅ | ✅ | ninguna |
| `domain-logic`, `project-context` | ✅ | ✅ | revisar vigencia |
| `tech-stack` | ✅ | ❌ | añadir (adaptado) |
| `debug-specialist` | ✅ | ❌ | añadir (adaptado) |
| `skill-authoring` | ✅ | ❌ | añadir (genérico) |
| `release-<project>` overlay | ✅ | ❌ | añadir (adaptado) |
| `AGENTS.md` documenta `[project].analyzer_command` | ✅ | ❌ | documentar |
| `forge.toml [project]` config-driven (propuesta) | pendiente | pendiente | adoptar cuando el framework lo soporte |
| Doc de adopción al día | n/a | ⚠️ `docs/AGENTIC_FORGE_ADOPTION.md` §6/§7 stale | actualizar |

**Diferencia legítima a respetar**: qgis-plugin-analyzer **usa `mypy`** (`pyproject.toml`
dev, `AGENTS.md` Quality Gates); su overlay de release **no** debe copiar el "skip mypy"
de ai-context-core. Además, su versión es **dinámica** (`src/analyzer/__init__.py:59`
deriva `__version__` de `pyproject.toml`), así que los sitios de versión son
**2** (`pyproject.toml:3` + `uv.lock`), no 3 como en ai-context-core.

## 2. Fase 1 — Overlay skills (`.agent-state/skills/`)

Se autodescubren: `opencode.json:skills.paths = [".agent/skills", ".agent-state/skills"]`
(requiere reiniciar opencode tras crearlas).

1. **`tech-stack/SKILL.md`** — adaptar a: Python `>=3.11`, `uv` (obligatorio),
   `ruff` (check+format), **`mypy`**, `pytest`; comandos exactos.
2. **`debug-specialist/SKILL.md`** — test de reproducción obligatorio antes de tocar
   código; validar con `uv run qgis-analyzer analyze . --max-cc 15` sin degradar
   `quality_score`/`maintainability`; limpiar `print`/debug antes de commit.
3. **`skill-authoring/SKILL.md`** — copia del genérico de ai-context-core (kebab-case,
   frontmatter `name/description/trigger`, degrees of freedom, checklist).
4. **`release-qgis-plugin-analyzer/SKILL.md`** — overlay de release sobre el
   `/release-package` genérico:
   - **Sitios de versión (2)**: `pyproject.toml` (`version`) + `uv.lock`; verificar
     `uv run qgis-analyzer --version`.
   - **Mantener `mypy`**: `uv run mypy src/`.
   - **PyPI manual**: parar en `python -m build` + `twine check`; el maintainer sube.
   - **`sync_metrics.py`** para refrescar `agent_metrics.json`.
   - Commit `chore(docs)` separado para artefactos regenerados
     (`AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`).
   - `git add` completo (`src/`, `tests/`, `AGENTS.md`, `forge.toml`, `.agent-state/`, `docs/`).

**Criterio de aceptación**: `forge validate` reporta **9 framework + 6 overlay = 15 skills**.

## 3. Fase 2 — `AGENTS.md`

- Tabla "Project overlay skills" (≈ línea 190): añadir las 4 skills nuevas
  (incluida `release-qgis-plugin-analyzer` — mejora respecto a ai-context-core, que
  no lista su release skill).
- Sección "Paths & Configuration" (≈ línea 229): documentar que
  `forge.toml [project].analyzer_command` (`uv run qgis-analyzer analyze . --max-cc 15`)
  es el hook de self-analysis para `/start-session` y `/audit-package`.
- Opcional: unificar nomenclatura de secciones con ai-context-core (p. ej. "Scoring"
  → "Metric Contract") solo si aporta claridad; no es bloqueante.

## 4. Fase 3 — `forge.toml` config-driven (condicional al framework)

Cuando `agentic-forge` implemente la propuesta
(`ai-context-core/docs/maintenance/agentic_forge_release_package_proposal.md`), adoptar:

```toml
[project]
version_files = ["pyproject.toml", "uv.lock"]
typecheck_command = "uv run mypy src/"
metrics_command = "uv run python scripts/sync_metrics.py"
pypi_manual = true
regenerated_artifacts = ["AI_CONTEXT.md", "PROJECT_SUMMARY.md", "project_context.json"]
```

Mientras el framework no soporte las claves, documentarlas en el skill de release
(Fase 1.4) y mantener el workflow genérico sin cambios.

## 5. Fase 4 — Documentación

- Actualizar `docs/AGENTIC_FORGE_ADOPTION.md` §6/§7: marcar **ai-context-core = hecho**
  (v5.1.0) y `qgis-plugin-manager = pendiente`; reflejar que el overlay de analyzer
  se alineó con el de ai-context-core.
- Registrar la sesión en `docs/DEVELOPMENT_LOG.md`.

## 6. Fase 5 — Validación

- `python .agent/tools/forge.py validate --graph` → 15 skills, 14 workflows, sin refs rotas.
- `python .agent/tools/forge.py validate --conflicts` → sin solapes de skills.
- Opcional (cross-repo): gate que confirme que los 3 repos pinnean `2de22cf`.
- Smoke: reiniciar opencode y verificar que las 4 skills nuevas se cargan.

## Orden de ejecución (checklist)

1. [ ] Fase 1.3 — `skill-authoring` (genérico).
2. [ ] Fase 1.1 — `tech-stack` (adaptado).
3. [ ] Fase 1.2 — `debug-specialist` (adaptado).
4. [ ] Fase 1.4 — `release-qgis-plugin-analyzer` (adaptado, con mypy).
5. [ ] Fase 2 — `AGENTS.md` (tabla de skills + hook `analyzer_command`).
6. [ ] Fase 4 — actualizar `docs/AGENTIC_FORGE_ADOPTION.md` + `DEVELOPMENT_LOG.md`.
7. [ ] Fase 5 — `forge validate --graph` + smoke.
8. [ ] (Diferido) Fase 3 — adoptar `[project]` config-driven cuando exista en el framework.

## Riesgos

- **Deriva con el framework**: crear overlay skills que deberían vivir en `agentic-forge`;
  mitigación: mantener en overlay solo lo project-specific (release, tech-stack, debug).
- **Duplicar `debug-specialist`/`skill-authoring`** si el framework los promueve;
  mitigación: si suben a `scaffold/`/framework, borrar los overlay y repuntar AGENTS.md.
- **Copiar "skip mypy"** de ai-context-core rompería el gate real de analyzer;
  mitigación: el overlay de release usa `mypy`, no lo omite.
- **Skills no cargadas** tras crearlas: requiere reiniciar opencode; documentarlo.

## Aprobación

- Propuesto; requiere aprobación explícita del USER (rol @architect) antes de implementar.
- Recomendado `/ia-critic` sobre este plan antes de ejecutar.
