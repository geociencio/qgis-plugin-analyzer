---
name: skill-authoring
description: Designing new agent skills with a clean structure, project-context integration, and high maintainability.
trigger: when creating new skills or standardizing procedures.
---

# Skill Authoring

Design predictable, reusable, and maintainable skills with a clear folder structure and production-ready logic.

## When to use this skill
- When the user asks to create a new skill.
- When a repeated process can be standardized.
- When converting a manual procedure into a reusable tool.

## Integration with Context
Any new skill must:
1. **Respect standards**: Reference @coding-standards when code is involved.
2. **Project context**: Consult @project-context for coherence with the architecture.
3. **Persistence**: Propose absolute paths within the workspace.

## Degrees of Freedom
1. **Strict**: Exact steps, terminal commands, technical scripts.
2. **Guided**: Templates for documents, folder structures, recommended flows.
3. **Creative**: Heuristics for brainstorming and design alternatives.

## Workflow
1. **Plan**: Define name (kebab-case), description (English), and triggers.
2. **Reference**: Identify existing skills the new skill must know.
3. **Structure**: Create the folder in `.agent-state/skills/`.
4. **Define**: Write `SKILL.md` with YAML frontmatter and markdown sections.
5. **Link**: Propose a `.agent/workflows/` entry if sequential and complex.
6. **Validate**: Apply the Quality Checklist.

## Anti-Patterns
- **Ambiguous language**: Use clear imperatives, not "could" or "maybe".
- **Redundancy**: Do not repeat global README information.
- **Folder inflation**: Do not create empty `resources/` or `scripts/` folders.
- **Language mixing**: `SKILL.md` in English; code and comments in English.

## Output (Exact Format)

**Folder:** `.agent-state/skills/<skill-name>/`

**SKILL.md:**
```markdown
---
name: <kebab-case>
description: <description in English, 3rd person, max 220 chars>
trigger: <when to use>
---
# <Skill Title>

## When to use this skill
- [Trigger 1]

## Degree of Freedom
- [Strict | Guided | Creative]

## Workflow
1. [Step 1]

## Instructions and Rules
- [Rule 1]

## Quality Checklist
- [ ] [Check]
```

## Error Handling
- If the result does not match the format, return to step 4 and adjust.
- If crucial technical info is missing, request access to specific files.
