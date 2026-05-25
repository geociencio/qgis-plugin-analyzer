---
description: Run qgis-analyzer on its own codebase for quality self-audit
agent: Agent Auditor
skills: [project-context, qa-standards]
validation: |
  - Verify analysis completes without errors
  - Confirm no critical/blocking issues
  - Review analysis_results/PROJECT_SUMMARY.md
---

# Workflow: Audit Plugin (Self-Analysis)

Runs the `qgis-plugin-analyzer` on its own source code to detect quality regressions, security issues, and standards violations.

### 1. Run Full Analysis
// turbo
```bash
uv run qgis-analyzer analyze . --profile release --strict
```

### 2. Review Results

🤖 **Agent Action**: Read and interpret the analysis output.

- Check `analysis_results/PROJECT_SUMMARY.md` for overall scores
- Review any `HIGH` or `CRITICAL` severity issues
- Compare scores against previous baseline in `.agent/memory/agent_metrics.json`

### 3. Triage Issues

| Severity | Action |
|----------|--------|
| CRITICAL | Fix immediately, block release |
| HIGH | Log in `task.md`, fix this session |
| MEDIUM | Log in `next_steps.md` for next phase |
| LOW | Accept or log as technical debt |

### 4. Update Metrics
After triage, update `.agent/memory/agent_metrics.json` with the new scores.

### Expected Results
- All tests passing
- Security score: 100/100
- Maintainability: ≥ 75/100
- No new CRITICAL or HIGH issues
