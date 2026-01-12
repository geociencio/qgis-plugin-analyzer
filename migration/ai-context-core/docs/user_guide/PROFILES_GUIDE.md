
# Profiles Guide

`ai-context-core` uses a powerful profile system to adapt its analysis to different types of Python projects. A "Profile" defines the rules, thresholds, and patterns that the analyzer looks for.

## 📂 Profile Location

Built-in profiles are located in `src/ai_context_core/config/profiles/`.
User-defined profiles can be added there or passed via configuration overrides.

## 📝 Anatomy of a Profile

A profile is a YAML file with three main sections:

### 1. `quality_weights`
Defines how much each metric contributes to the overall "Quality Score" (0-100).

```yaml
quality_weights:
  docstrings: 30       # Documentación vale 30 puntos
  complexity_low: 20   # Baja complejidad vale 20 puntos
  no_syntax_error: 30  # Código sin errores vale 30 puntos
  # ...
```

### 2. `thresholds`
Define the boundaries for metrics. What is "too complex" or "too large" depends on the project type.

```yaml
thresholds:
  complexity_high: 25  # Más de 25 CC es 'alto'
  size_small: 200      # Menos de 200 líneas es 'pequeño'
```

### 3. `patterns`
Enables or disables specific detection logic modules.

```yaml
patterns:
  qgis_compliance:     # Reglas específicas para QGIS
    enabled: true
    mandatory_files:
      - "metadata.txt"
      - "__init__.py"
  linter:
    enabled: true      # Integración con Ruff
```

## 🚀 Creating a Custom Profile

1.  Create a new YAML file, e.g., `flask-microservice.yaml`.
2.  Define your overrides (you don't need to copy everything, just what changes from `defaults.yaml`).

**Example `flask-microservice.yaml`**:
```yaml
profile_name: "flask-microservice"
description: "Strict profile for high-performance microservices"

thresholds:
  complexity_high: 10  # Stricter: functions shouldn't be complex
  size_small: 100      # Smaller files preferred

patterns:
  qgis_compliance:
    enabled: false
```

3.  Use it via CLI:
    ```bash
    ai-ctx init --profile flask-microservice
    ```
    *(Note: For now, custom profiles need to be in the source tree or manually configured in `.ai-context/config.yaml`)*.
