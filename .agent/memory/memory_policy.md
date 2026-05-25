# Memory Policy — qgis-plugin-analyzer

> Defines the lifecycle, retention, and pruning rules for the agentic memory system.

## 3-Tier Memory Model

### Tier 1: Episodic Memory (Session Logs)
- **Location**: `docs/maintenance/session_YYYY-MM-DD_[topic].md`
- **Purpose**: Full session summaries, decisions, and outcomes
- **Retention**: Indefinite (historical archive)
- **Pruning**: Manual review every 6 months

### Tier 2: Semantic Memory (Lessons)
- **Location**: `.agent/memory/AGENT_LESSONS.md`
- **Format**: YAML-structured entries with `date`, `category`, `topic`, `lesson`, `action`
- **Purpose**: Distilled technical patterns, user preferences, and reusable solutions
- **Retention**: Active for 90 days, then marked `[consolidated]` if reflected in a `SKILL.md`
- **Pruning**: Lessons marked `[consolidated]` are moved to `[PRUNED]` index on next review

### Tier 3: Long-Term Archive (Metrics)
- **Location**: `.agent/memory/agent_metrics.json`
- **Purpose**: Structured quality metrics across sessions for trend analysis
- **Retention**: Indefinite
- **Pruning**: None — metrics accumulate as time series

## Lesson Lifecycle

```
New lesson → AGENT_LESSONS.md (ACTIVE)
    ↓ 90 days
Reflected in SKILL.md? → YES → Mark [consolidated]
                       → NO  → Keep active
    ↓ Next review
[consolidated] entries → Move to [PRUNED] index
```

## Session Lifecycle

```
Session start → /start-session reads AGENT_LESSONS.md + agent_metrics.json
Session work   → Agent extracts patterns
Session close  → /close-session adds 3 lessons to AGENT_LESSONS.md
               → Archive next_steps.md to history/
               → Create session log in docs/maintenance/
               → Update agent_metrics.json
```

## Metric Tracking

`agent_metrics.json` records per-session snapshots:
- `date`: ISO date
- `session`: session topic
- `scores`: stability, maintainability, security
- `tests`: pass count, total count
- `issues`: count by severity

## Pruning Schedule

- **After each session**: Archive `next_steps.md` to history
- **Every 90 days**: Review `AGENT_LESSONS.md` for consolidation
- **Every 6 months**: Review episodic memory for relevance
