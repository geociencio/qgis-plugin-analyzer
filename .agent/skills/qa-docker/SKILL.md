---
name: qa-docker
description: Estándares para pruebas y aseguramiento de calidad.
trigger: al escribir o ejecutar tests, usar mocks o depurar fallos en CI.
---

# QA y Automatización

Garantiza la estabilidad del código mediante testing riguroso, uso de mocks para dependencias de QGIS (cuando sea necesario) y ejecución en entornos limpios.

## Cuándo usar este skill
- Al crear nuevos casos de prueba unitarios o de integración.
- Al depurar fallos en los tests.
- Al configurar o modificar la estrategia de testing.

## Grado de Libertad
- **Guiado**: Se deben seguir las estrategias de testing definidas (Pytest).

## Workflow
1. **Diseño**: Tests unitarios para lógica pura (analyzer core).
2. **Implementación**: Usar `pytest` y fixtures.
3. **Ejecución**: `uv run pytest`.
4. **Cobertura**: Mantener cobertura alta en módulos críticos (`src/analyzer`).

## Instrucciones y Reglas

### Estrategia de Mocking
- Para código que importa `qgis.core` o `qgis.gui`, usar estrategias de mocking (ej. `unittest.mock` o `pytest-mock`) si no se está ejecutando dentro de un entorno QGIS real.
- El proyecto usa `qgis-stubs` para tipado, pero en runtime necesitará mocks o QGIS real.

### Comandos
- **Test completos**: `uv run pytest`
- **Linting**: `uv run ruff check .`
- **Type Check**: `uv run mypy .`

## Checklist de Calidad
- [ ] ¿Los nuevos tests cubren los casos de borde?
- [ ] ¿Pasan `mypy` y `ruff` sin errores?
- [ ] ¿Se han añadido tests para regresiones encontradas?
