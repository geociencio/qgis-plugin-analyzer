# ANÁLISIS INICIAL DE PROYECTO PARA IA

## DATOS DEL PROYECTO:
- Nombre: qgis-plugin-analyzer
- Tipo: CLI Tool / Static Analyzer
- Tamaño: 24 módulos, ~4.4k líneas
- Python: 3.8+

## OBJETIVO DEL ANÁLISIS:
[ ] Identificar arquitectura
[ ] Evaluar calidad de código
[ ] Detectar deuda técnica
[ ] Sugerir optimizaciones
[ ] Crear plan de refactorización

## ARCHIVOS PROVISIONADOS:
Adjunto/Proporciono:
1. `project_structure.txt` - Árbol de directorios
2. `main_modules.py` - Módulos principales (engine.py, scanner.py, fixer.py)
3. `requirements.txt` - Dependencias (zero runtime deps)
4. `entry_points.txt` - CLI entry point (qgis-analyzer)

## PREGUNTAS ESPECÍFICAS:

1. **ARQUITECTURA**: ¿Qué patrones arquitectónicos detectas?
2. **CALIDAD**: ¿Cuáles son los mayores problemas de calidad?
3. **MANTENIBILIDAD**: ¿Qué haría más mantenible el código?
4. **PERFORMANCE**: ¿Oportunidades de optimización evidentes?
5. **REFACTORIZACIÓN**: ¿Por dónde comenzarías y por qué?

## FORMATO DE RESPUESTA REQUERIDO:

```
architecture
[Descripción de la arquitectura en 1-2 párrafos]
quality_assessment
- Fortalezas: [lista]
- Debilidades: [lista]
- Riesgos: [lista]
technical_debt
1. [Item 1] - Prioridad: Alta/Media/Baja
2. [Item 2] - Prioridad: Alta/Media/Baja
optimization_plan
## FASE 1 (Inmediata):
- [Acción 1]
- [Acción 2]

## FASE 2 (Corto plazo):
- [Acción 1]
- [Acción 2]

## FASE 3 (Largo plazo):
- [Acción 1]
- [Acción 2]
context_for_future
[Contexto persistente de 10-15 líneas para futuras consultas]
## RESTRICCIONES:
- **REGLAS DE NEGOCIO**: El analizador debe detectar y sugerir escapar % como %% en metadata.txt de plugins QGIS.
- **INDEPENDENCIA**: El analizador NO debe depender de PyQGIS/Qt en runtime.
Máximo 5000 tokens por respuesta

Enfocarse en Python 3.8+

Priorizar soluciones prácticas

Considerar mantenibilidad a largo plazo

'''

