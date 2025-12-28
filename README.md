# QGIS Plugin Analyzer 🛡️

El **QGIS Plugin Analyzer** es una herramienta de análisis estático diseñada específicamente para desarrolladores de plugins de QGIS (PyQGIS). Su objetivo es elevar la calidad de los plugins, asegurando que cumplan con las mejores prácticas de la comunidad y estén optimizados para el desarrollo asistido por IA.

## ✨ Características Principales

- **Auditoría de Estándares QGIS**: Detecta falta de internacionalización (i18n), uso de APIs obsoletas, y riesgos de seguridad en hilos (Threading). Ver [Catálogo de Reglas](RULES.md).
- **Análisis de Arquitectura**: Identifica violaciones en la separación de responsabilidades (Core vs GUI).
- **Métricas de Calidad**: Calcula complejidad ciclomática y cobertura de documentación.
- **Preparado para IA**: Genera resúmenes estructurados y contextos optimizados para LLMs.
- **Alto Rendimiento**: Utiliza procesamiento paralelo para analizar proyectos grandes en segundos.

## ⚖️ ¿Por qué usar este Analizador? (Comparativa)

| Característica | QGIS Plugin Analyzer | flake8-qgis | qgis-plugin-dev-tools | Official Repo Bot |
| :--- | :---: | :---: | :---: | :---: |
| **Linting Estático** | ✅ (Reglas Propias) | ✅ (Estricto) | ❌ | ✅ (Limitado) |
| **Complejidad (AST)** | ✅ | ❌ | ❌ | ❌ |
| **Auditoría i18n QGIS** | ✅ | ❌ | ❌ | ✅ |
| **Auditoría Arquitectura**| ✅ (UI/Core) | ❌ | ❌ | ❌ |
| **Reglas de Rendimiento** | ✅ (Spatial Index) | ✅ | ❌ | ❌ |
| **Escaneo de Seguridad** | ✅ | ❌ | ❌ | ✅ (Malware) |
| **Generación Contexto IA**| ✅ | ❌ | ❌ | ❌ |
| **Soporte Multiproceso**  | ✅ | ❌ | ❌ | ❌ |
| **Reportes Externos**    | ✅ (MD, JSON) | ❌ | ✅ (Packaging) | ❌ |

### Diferenciadores Clave

1.  **Puntuación de Calidad Holística**: A diferencia de los linters que solo reportan errores, el Analyzer proporciona una **Puntuación de Calidad (0-100)**.
2.  **Infraestructura Nativa para IA**: Genera un "Cerebro de Proyecto" estructurado que permite a asistentes de IA (ChatGPT/Gemini) dar sugerencias de refactorización mucho más precisas.
3.  **Cumplimiento de Arquitectura**: Detecta violaciones de patrones (ej. lógica pesada en la UI), la causa #1 de deuda técnica en plugins.
4.  **Independencia Total**: Puede ejecutarse en cualquier proyecto sin formar parte de él, manteniendo el repositorio del plugin limpio.

## 🚀 Instalación y Uso

### Instalación local (desarrollo):
```bash
git clone https://github.com/tu-usuario/qgis-plugin-analyzer
cd qgis-plugin-analyzer
pip install -e .
```

### Ejecutar análisis:
```bash
qgis-analyzer /ruta/a/tu/plugin -o ./reporte_calidad
```

## 📊 Reportes Generados

- `PROJECT_SUMMARY.md`: Resumen ejecutivo con puntuación de calidad y hallazgos críticos.
- `project_context.json`: Datos estructurados completos para integraciones externas.

## 📚 Referencias y Estándares

El desarrollo de este analizador se basa en las directrices oficiales de la comunidad de QGIS y estándares de la industria:

- **[PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)**: La biblia para el desarrollo de plugins en Python.
- **[QGIS Plugin Repository Requirements](https://plugins.qgis.org/publish/)**: Criterios oficiales para la aprobación de plugins en el repositorio oficial.
- **[QGIS Coding Standards](https://docs.qgis.org/latest/en/docs/developer_guide/codingstandards.html)**: Estándares de estilo y organización de código de QGIS.
- **[QGIS HIG (Human Interface Guidelines)](https://docs.qgis.org/latest/en/docs/developer_guide/hig.html)**: Guía para el diseño de interfaces de usuario consistentes.
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Estándar para mensajes de commit claros y estructurados.

## 🛠️ Contribuir
Las reglas de auditoría se encuentran en `src/analyzer/scanner.py`. ¡Siéntete libre de añadir nuevas reglas siguiendo el patrón existente!

---
*Desarrollado para el equipo de SecInterp y la comunidad de QGIS.*
