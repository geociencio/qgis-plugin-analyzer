# qgis-plugin-analyzer Agentic System — Gen 5→6 → Gen 8 (opencode-native)

> **Created**: 2026-09-14
> **Status**: ✅ Executed (Phases A–D). E–F remain as follow-ups.
> **Target runtime**: opencode (deepseek-v4-pro)
> **Basis**: port of the SecInterp Gen 7 → Gen 8 evolution, re-scoped for this Python static-analysis package (not a QGIS plugin).

---

## 0. Premise

The prior Gen 5→6 system (`IMPROVEMENT_PLAN.md`) modeled a dual Antigravity/CodeWhale runtime. The real runtime is **opencode**. The bridge layer — `.codewhale/instructions.md`, `skill_sync.py`, `init_agent_system.sh` — was already one generation stale. Per the "Bitter Lesson", the bridge had become the debt, not the solution.

**Gen 8 governing principle**: stop bridging runtimes; use opencode-native mechanisms only — root `AGENTS.md`, `SKILL.md` (`name`+`description`), `opencode.json` (subagents + `skills.paths`). Any script that exists only to translate between runtimes is retired.

---

## 1. Roadmap

### Phase A — Unify AGENTS.md ✅ DONE
- [x] Create root `AGENTS.md` as the single source of truth (roles, workflows table, skills table, build commands, architecture, quality gates).
- [x] Convert `.agent/AGENTS.md` to a compatibility pointer.
- [x] Retire `skill_sync.py` (both `.agent/scripts/` and `scripts/`) + `init_agent_system.sh`.

### Phase B — Consolidate tooling ✅ DONE
- [x] Retire `.codewhale/instructions.md` (CodeWhale bridge).
- [x] Add `scripts/memory_prune.py` (prune expired snapshots + report stale lessons).
- [x] Add `scripts/validate_agent_system.py` (skills/workflows/AGENTS.md consistency gate, `--graph`).
- [x] Keep `scripts/sync_metrics.py` (self-analysis → `agent_metrics.json`) as the single metric entry point.

### Phase C — Externalize thresholds 🟡 FOLLOW-UP
- [ ] CC / module-size thresholds currently live in the analyzer itself (`scoring.py`). Externalize if a self-audit gate is added to CI (out of scope for this port).

### Phase D — Native opencode subagents ✅ DONE
- [x] Create `opencode.json` with inline `agent` definitions: `architect` (`edit: allow`), `qa_engineer` (`edit: ask`), `auditor` (`edit: deny`).
- [x] Register `.agent/skills` via `skills.paths`.
- [x] Normalize workflow `agent:` frontmatter to the 3 ids (was 4 inconsistent labels).

### Phase E — Standard skill format 🟡 PARTIAL
- [x] Add missing `name`/`description` frontmatter to `i18n-standards/SKILL.md`.
- [ ] Drop the custom `trigger` field from all `SKILL.md` files and fold "when to use" into `description` (low ROI; `trigger` is now informational only, since `skill_sync.py` was retired).

### Phase F — Session-as-durable-object 📋 PROPOSAL ONLY
- [ ] Migrate Markdown session logs (`docs/maintenance/`) to a durable object store (JSONL). Requires its own migration plan; not scheduled.

---

## 2. Success criteria

| Criterion | Before (Gen 5→6) | After (Gen 8) |
|---|---|---|
| AGENTS.md | `.agent/AGENTS.md` canonical (absolute paths) | root `AGENTS.md` SSoT + pointer |
| Runtimes modeled | antigravity + codewhale | opencode native |
| Roles | prose | subagents with permission gradient |
| Skill table | auto-generated via `skill_sync.py` | manually maintained, relative paths |
| Bridge files | `.codewhale/`, `skill_sync.py` | retired |
| Agent tooling | 1 script (`skill_sync.py`) | `validate_agent_system.py` + `memory_prune.py` + `sync_metrics.py` |

---

## 3. Decisions (confirmed)

1. `skill_sync.py` → **eliminate** (opencode indexes skills natively).
2. `.codewhale/instructions.md` + `init_agent_system.sh` → **eliminate** (runtime bridge).
3. Agent tooling → **root `scripts/`** (matches SecInterp; `.agent/scripts/` removed).
4. Workflow `agent:` → **normalize to 3 ids**.
5. Document language → **English**.

---

## 4. References

- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- Anthropic — [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)
- opencode — [Agent Skills](https://opencode.ai/docs/skills/)
- Supersedes: `.agent/architecture/IMPROVEMENT_PLAN.md` (Gen 5→6, kept as reference)
- Source of truth port: `sec_interp/.agent/architecture/IMPROVEMENT_PLAN_GEN8.md`

---

*Executed 2026-09-14. Phases C (partial), E (partial), and F remain open.*
