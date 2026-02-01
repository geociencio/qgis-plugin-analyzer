---
description: Audita la consistencia del sistema agentico.
agent: Static Analysis Architect
skills: [project-context]
validation:
  - Skills con estructura válida
  - Workflows con metadata correcta
---

Verifica que el "cerebro" del proyecto esté sano.

1. **Auditoría de Skills**:
   Revisar `.agent/skills/` para asegurar que tienen `SKILL.md` con frontmatter YAML válido.

2. **Auditoría de Workflows**:
   Revisar `.agent/workflows/` para asegurar que apuntan a Agentes y Skills existentes.

3. **Reporte**:
   Generar lista de inconsistencias si las hay.
