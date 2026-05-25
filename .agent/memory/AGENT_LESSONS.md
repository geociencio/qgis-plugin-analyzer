# Agent Learning Memory (qgis-plugin-analyzer)

This file records technical lessons, user preferences, and solutions to complex problems.
It uses a structured format for efficient retrieval by the agent system.

**Memory Policy**: Lessons older than 90 days that are already reflected in a `SKILL.md`
are marked `[consolidated]` and will be pruned in the next review cycle.
See `.agent/memory/memory_policy.md` for the full policy.

---

## Lesson Log (YAML Structured)

```yaml
lessons:

  # --- ACTIVE LESSONS (< 90 days or not yet in a SKILL.md) ---
  - date: '2026-05-25'
    category: RELEASE
    topic: Setuptools License Deprecation
    lesson: 'setuptools emits deprecation warnings for TOML table license format
      and License classifiers. pyproject.toml should use SPDX expression string
      (license = {text = "GPL-3.0-or-later"}) and remove the classifier entry.'
    action: 'Deferred to next session. Non-blocking for builds until 2027-Feb-18.'
  - date: '2026-05-25'
    category: AGENTIC_SYSTEM
    topic: I18n Visitor False Positives
    lesson: 'The I18nVisitor heuristic (is_translatable_string) creates the illusion
      that self.tr() is recognized, when in reality both self.tr() and
      QCoreApplication.translate() are equally flagged. Short Qt widget labels
      (OK, Cancel, Save) pass through the heuristic while longer descriptive
      strings used with QCoreApplication.translate() do not. The fix adds a
      dedicated I18N_WRAPPER_FUNCTIONS set and _in_i18n_wrapper state tracking.'
    action: 'Added I18N_WRAPPER_FUNCTIONS = {"tr", "translate"} to I18nVisitor.
      Commit: ddf12b7.'

  - date: '2026-05-25'
    category: AGENTIC_SYSTEM
    topic: Agentic System Gen 5→6 Upgrade
    lesson: 'The .agent/ system was at Gen 5 with stale active documents, no
      observability, and no runtime bridge. sec_interp (Gen 6→7) provides a
      clear upgrade path: workflows/index.md for CodeWhale adaptation,
      sync_metrics.py for automated metric extraction, 3-tier memory model,
      and architecture/IMPROVEMENT_PLAN.md for roadmap tracking.'
    action: 'Created architecture/, memory_policy.md, agent_metrics.json,
      workflows/index.md, audit-plugin workflow, i18n-standards skill,
      .agent/README.md. Reactivated task.md and next_steps.md.'

  - date: '2026-04-26'
    category: TECHNICAL
    topic: Scoring Engine AST Integration
    lesson: 'AST-based scoring engines must explicitly incorporate internal rule
      violations (e.g., QGIS compliance) into the maintainability index to
      avoid over-optimistic health scores.'
    action: 'Fixed in v1.13.0. Score corrected from 99.9 to ~77.0.'

  - date: '2026-04-26'
    category: TECHNICAL
    topic: Package Shadowing Resolution
    lesson: 'Renaming entry points like cli.py to main.py is necessary when a
      package shares the same name to resolve circular dependency false
      positives in semantic analysis.'
    action: 'Applied in v1.13.0.'

  - date: '2026-04-26'
    category: AGENTIC_SYSTEM
    topic: Agentic System Localization
    lesson: 'Standardizing the agentic system to English and generic Python
      lifecycle improves architectural clarity and simplifies release
      workflows across different runtime environments.'

  - date: '2026-04-05'
    category: TECHNICAL
    topic: Skill Sync Automation
    lesson: 'When upgrading agentic frameworks, use skill_sync.py to regenerate
      the dynamic triggers in AGENTS.md automatically.'

  - date: '2026-04-05'
    category: TECHNICAL
    topic: Ruff Type Hint Modernization
    lesson: 'Ruff --fix handles type hint deprecations proactively (List to
      list), validating PEP 585 compliance natively.'
```
