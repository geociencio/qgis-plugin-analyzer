---
name: project-context
description: Resumen del propósito, arquitectura y estructura del proyecto qgis-plugin-analyzer.
trigger: al iniciar nuevas tareas, solicitar resúmenes o explicar la arquitectura del analizador.
---

# Contexto del Proyecto qgis-plugin-analyzer

Herramienta de análisis estático diseñada específicamente para Plugins de QGIS (PyQGIS). Ayuda a desarrolladores a mantener estándares de calidad, seguridad y compatibilidad.

## Cuándo usar este skill
- Al inicio de una sesión para refrescar la arquitectura.
- Al proponer cambios estructurales en el motor de análisis.
- Cuando el usuario solicita un estado actual del proyecto.

## Arquitectura

### Core (`src/analyzer`)
El núcleo de la aplicación.
- **Scanner**: Recorre directorios y archivos.
- **Parser**: Analiza código Python, metadatos y estructura.
- **Rules**: Definición de reglas de calidad y compatibilidad QGIS.
- **Report**: Generación de reportes (HTML, JSON, Markdown).

### Interfaz
- **CLI**: Punto de entrada principal (`analyzer/cli.py`).

### Filosofía
- **Lightweight**: No requiere una instalación completa de QGIS para correr análisis básicos (usa AST y regex donde es posible).
- **Extensible**: Fácil de añadir nuevas reglas.
- **Agentic-Ready**: Diseñado para ser usado por agentes de IA para validar código.

## Estructura de Carpetas
- `src/analyzer`: Código fuente.
- `tests/`: Suite de pruebas (pytest).
- `.agent/`: Configuración del sistema agentico.
- `docs/`: Documentación del usuario.

## Checklist de Calidad para Contribuciones
- [ ] ¿El cambio mantiene la compatibilidad con versiones antiguas de Python (3.8+)?
- [ ] ¿Se han añadido tests para las nuevas reglas de análisis?
