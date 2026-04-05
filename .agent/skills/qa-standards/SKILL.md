---
name: qa-standards
description: Standards for automated testing, CI/CD, and the use of Mocks.
trigger: when writing or executing tests, designing testing strategies, or managing testing infrastructure.
---

# QA and Automation Standards

Ensures code stability through a controlled execution environment, simulation strategies (Mocks), and CI/CD practices.

## When to use this skill
- When creating new unit or integration test cases.
- When debugging failures in the CI/CD pipeline.
- When configuring or modifying the testing environment.

## Degree of Freedom
- **Guided**: Follow the testing strategies defined for the project, aiming for high coverage and isolation.

## Workflow
1. **Design**: Apply "Test-Driven Development (TDD)" or "Behaviour-Driven Development (BDD)" strategies as appropriate for the project.
2. **Implementation**: Create tests using the project's primary framework (e.g., `pytest`, `unittest`, `jest`, etc.). Isolate external dependencies using Mocks.
3. **Execution**: Validate locally using the Local Test Runner and then in the CI/CD environment.
4. **Coverage**: Verify that the minimum required coverage is achieved (> 80%).

## Instructions and Rules

### Testing Strategy
- **Isolation**: Unit tests must run quickly and without external dependencies (databases, network, UI).
- **Mocks**: Simulate (mock) external services and complex third-party libraries. Rigorously clean up mocks after each test.
- **Integration**: Integration tests must validate the complete flow in an environment as close as possible to production (e.g., Docker containers).

### Testing Environment
- **Consistency**: The main test command (`{{TEST_COMMAND}}`) must be the definitive health check. If it passes locally, it must pass in CI/CD.
- **Cleanup**: Avoid leaving residual state in the environment from tests.

## Quality Checklist
- [ ] Is the coverage of new services satisfactory (> 80%)?
- [ ] Are patches/Mocks cleaned up after each test?
- [ ] Can unit tests be executed in isolation without starting heavy services?
- [ ] Does the testing environment report zero failures?
