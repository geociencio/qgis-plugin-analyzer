---
name: qa-docker
description: Standards for testing and quality assurance using Docker environments.
trigger: when running integration tests or validating the package in clean environments
---

# QA & Docker Standards

Ensures that `qgis-plugin-analyzer` works correctly across different environments and Python versions by using isolated Docker containers.

## Core Principles
- **Isolation**: Tests must run in clean environments to avoid "works on my machine" issues.
- **Reproducibility**: Dockerfiles must be versioned and stable.
- **Multi-version**: Validate against multiple Python versions (3.9 to 3.12).

## Docker Workflow

### 1. Build Verification
To verify the package in a clean environment:
```bash
docker build -t qgis-analyzer-qa -f docker/QA.Dockerfile .
```

### 2. Integration Tests
Run the suite inside a container:
```bash
docker run --rm qgis-analyzer-qa pytest
```

### 3. CLI Validation
Ensure the installed package works correctly:
```bash
docker run --rm qgis-analyzer-qa qgis-analyzer --version
```

## Standards for Dockerfiles
- Use official `python:3.x-slim` images to minimize size.
- Install `uv` for fast dependency management.
- Copy only necessary files (use `.dockerignore`).

## Quality Gates
- All tests must pass in the Docker container.
- No permission issues when running as a non-root user.
- Package size must be within expected limits.
