---
name: domain-logic
description: Standards for handling business logic, data validation, and 3-level validation architecture.
trigger: when implementing new business rules, data validation, or core processing logic.
---

# Domain and Business Logic

Defines the business rules for processing application-specific data, ensuring consistency and integrity through a multi-layered validation approach.

## When to use this skill
- When modifying core business services.
- When designing algorithms or data processing pipelines.
- When implementing new validation rules.

## Degree of Freedom
- **Strict**: 3-level validation rules and core-UI decoupling are mandatory.

## Workflow
1. **Modeling**: Define entities using Dataclasses and strict types.
2. **Validation**: Implement the 3 levels (Type, Schema, Business).
3. **Abstraction**: Ensure core logic is independent of UI or specialized framework elements.
4. **Testing**: Create unit tests for all domain logic.

## Instructions and Rules

### 3-Level Validation
1. **Level 1 (Type)**: Basic data types and allowed ranges.
2. **Level 2 (Schema)**: Consistency between fields in a single DTO.
3. **Level 3 (Business)**: External consistency and cross-module rules.

### Decoupling Rules
- **Pure Core**: Core services MUST NEVER depend on UI libraries or specific framework graphics components.
- **DTOs**: Operate with clean Data Transfer Objects; convert to specialized framework objects only at the boundaries.
- **Mocks**: Use mocks for all external dependencies in local unit tests.

## Quality Checklist
- [ ] Is core logic independent of the UI or specialized libraries?
- [ ] Are all 3 validation levels implemented?
- [ ] Do tests exist for edge cases?
- [ ] Are project units handled correctly?

## I18n Visitor (analyzer-specific)

The analyzer audits i18n in target plugins; its own `I18nVisitor`
(`src/analyzer/visitors/i18n_visitor.py`) recognizes these translation wrappers:
- `self.tr("...")` — QObject translation
- `QCoreApplication.translate("Context", "...")` — non-QObject contexts
- `QObject.translate("Context", "...")` — equivalent to QCoreApplication

The `is_translatable_string()` heuristic:
- requires length ≥ 3 characters
- skips paths (`/`, `\`, `:/`)
- skips snake_case / CamelCase / UPPERCASE identifiers
- skips technical keywords (`name`, `type`, `value`, ...)
- flags strings with spaces or terminal punctuation (`:.!?`)

False-positive prevention: strings inside `tr()`/`translate()` and format chains
(`QCoreApplication.translate("Ctx", "Found {}").format(n)`) are correctly skipped.

When modifying the visitor, add tests to `tests/test_i18n_wrappers.py` and
`tests/test_i18n_heuristics.py`, and keep rule IDs stable (e.g. `MISSING_I18N`).
