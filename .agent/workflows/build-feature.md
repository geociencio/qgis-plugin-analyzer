---
description: Start the Autonomous AI Developer Pipeline sequence for a new feature.
agent: Architect
skills: [domain-logic, qa-docker, coding-standards]
---
# Build Feature Autonomous Pipeline

When the user types `/build-feature <requirement>`, orchestrate the development process strictly using `.agent/AGENTS.md` and the modular `.agent/skills/`.

### Execution Sequence:

1. **Strategic Planning Mode**
   Act as the **@architect**. Deeply analyze the `<requirement>`. Use the `domain-logic` and `coding-standards` skills to draft a robust implementation plan.
   - **Important**: Save this plan as `docs/plans/Technical_Specification.md`.
   - **Approval Gate**: You MUST pause execution and eagerly ask the user: "Do you approve of this architecture? You can add comments directly to `Technical_Specification.md` if you want me to rethink any part."
   *(Wait for the user to explicitly type "Approved" or apply their requested feedback before moving to step 2).*

1.5. **Technical Critique (Architect vs. Auditor) 🤖**
   - **Agent Reflection**: Activate the **@auditor** role.
   - **Challenge the Plan**: Identify 3 potential failure points or edge cases in the proposed strategy.
   - **Mitigation**: The @architect must address these points before presenting the plan to the user.
   - **Hallucination Hunt**: Verify that all proposed tool calls and file paths are valid.

2. **Autonomous Execution Phase**
   Shift context. Act as the **@architect** again (now acting as the developer), but strictly follow the approved `Technical_Specification.md`.
   - Write the backend logic and CLI components according to the project standards.
   - Ensure the code adheres perfectly to modern Python best practices (typing, pathlib, ruff).

3. **Autonomous QA & Bug-Hunting Phase**
   Shift context. Act as the **@qa_engineer**.
   - Write the corresponding isolated unit tests or integration tests.
   - You MUST run the test suite (locally or via Docker) to guarantee system integrity.
   - Find and fix any dependency mismatches, unhandled errors, or edge cases. Do not stop until all tests pass.

4. **Integration & Handover**
   Shift context to the **@auditor**.
   - Review that the code maintains the `.agent/AGENTS.md` metrics (such as complexity limits and documentation coverage).
   - Once successfully checked, generate an output confirming the feature is ready to be committed!
