# QGIS Plugin Analyzer 🛡️
![GitHub release (latest by date)](https://img.shields.io/github/v/release/geociencio/qgis-plugin-analyzer?color=blue&logo=github)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/github/license/geociencio/qgis-plugin-analyzer?color=green)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?logo=git)

The **QGIS Plugin Analyzer** is a static analysis tool designed specifically for QGIS (PyQGIS) plugin developers. Its goal is to elevate plugin quality by ensuring they follow community best practices and are optimized for AI-assisted development.

## ✨ Main Features

- **Análisis de Ruff Integrado**: Combina reglas personalizadas de QGIS con el linter más rápido del ecosistema Python.
- **Generación de Boilerplate (`init`)**: Crea estructuras de plugins profesionales (`processing`, `gui`, `map_tool`) al instante.
- **AI-Ready**: Genera resúmenes estructurados y contextos optimizados para LLMs.
- **Reportes HTML**: Visualización profesional de la salud del plugin.
- **Alto Rendimiento**: Procesamiento en paralelo para analizar proyectos grandes en segundos.
- **Selective Auditing**: Support for `.analyzerignore` to exclude specific files or directories from analysis.

## ⚖️ Why use this Analyzer? (Comparison)

| Feature | **QGIS Plugin Analyzer** | flake8-qgis | Ruff (Standard) | Official Repo Bot |
| :--- | :---: | :---: | :---: | :---: |
| **Static Linting** | ✅ (Ruff + Custom) | ✅ (flake8) | ✅ (General) | ✅ (Limited) |
| **QGIS-Specific Rules**| ✅ (Precise AST) | ✅ (Regex/AST) | ❌ | ✅ |
| **Speed (Rust/Parallel)**| ✅ | ❌ | ✅ | ❌ |
| **Project Templating** | ✅ (`init`) | ❌ | ❌ | ❌ |
| **i18n / API Audit** | ✅ | ❌ | ❌ | ✅ |
| **Architecture Audit** | ✅ (UI/Core) | ❌ | ❌ | ❌ |
| **HTML/MD Reports** | ✅ | ❌ | ❌ | ❌ |
| **AI Context Gen** | ✅ (Project Brain) | ❌ | ❌ | ❌ |
| **Strict CI Profiles** | ✅ | ❌ | ✅ | ❌ |

### Key Differentiators

1.  **Motor Híbrido de Máximo Rendimiento**: Combina el motor Rust de **Ruff** (para reglas PEP8) con nuestro motor **AST** (para reglas PyQGIS), ofreciendo una velocidad hasta 100 veces superior a linters tradicionales.
2.  **Generación de Boilerplate Inteligente**: A diferencia de otras herramientas que se centran en el análisis, el comando `init` permite crear plugins "AI-Ready" desde el primer segundo.
3.  **Auditoría de Arquitectura**: Único en detectar violaciones de patrones (como lógica pesada en la UI), la causa #1 de deuda técnica en plugins complejos.
4.  **Infraestructura para IA (Project Brain)**: Genera resúmenes técnicos optimizados para que asistentes como ChatGPT o Gemini entiendan tu código al instante.
5.  **Listo para CI/CD**: Los perfiles de configuración permiten integrar fallos de cumplimiento directamente en tus pipelines de GitHub Actions.

## 🚀 Installation and Usage

### Installation with `uv` (Recommended):

If you have [uv](https://github.com/astral-sh/uv) installed, you can install the analyzer quickly and in isolation:

**1. As a global tool (isolated):**
```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-analyzer.git
```

**2. Local installation for development:**
```bash
git clone https://github.com/geociencio/qgis-plugin-analyzer
cd qgis-plugin-analyzer
uv sync
```

### Installation with `pip`:
```bash
pip install .
```

### Comandos Principales:

**1. Analizar un Plugin:**
```bash
qgis-analyzer analyze /path/to/your/plugin -o ./quality_report
```

**2. Crear un Plugin desde Plantilla:**
```bash
qgis-analyzer init my_new_plugin --type map_tool --name "Herramienta Pro"
```

**3. Soporte Legacy:**
El comando por defecto sigue siendo el análisis si no se especifica subcomando:
```bash
qgis-analyzer /path/to/your/plugin
```

## 📊 Generated Reports

- `PROJECT_SUMMARY.md`: Executive summary with quality score and critical findings.
- `project_context.json`: Full structured data for external integrations.

## 📚 References and Standards

The development of this analyzer is based on official QGIS community guidelines and industry standards:

- **[PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)**: The bible for Python plugin development.
- **[QGIS Plugin Repository Requirements](https://plugins.qgis.org/publish/)**: Official criteria for plugin approval in the official repository.
- **[QGIS Coding Standards](https://docs.qgis.org/latest/en/docs/developer_guide/codingstandards.html)**: Style and code organization standards for QGIS.
- **[QGIS HIG (Human Interface Guidelines)](https://docs.qgis.org/latest/en/docs/developer_guide/hig.html)**: Guide for designing consistent user interfaces.
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Standard for clear and structured commit messages.

## 🛠️ Contributing
Audit rules are located in `src/analyzer/scanner.py`. Feel free to add new rules following the existing pattern!

---
*Developed for the SecInterp team and the QGIS community.*
