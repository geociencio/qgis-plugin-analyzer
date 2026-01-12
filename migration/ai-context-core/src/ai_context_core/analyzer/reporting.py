
import pathlib
import time
import json
from typing import Dict, Any, List

def generate_mermaid_graph(dependencies: Dict[str, Any]) -> str:
    """Genera diagrama Mermaid de dependencias principales."""
    graph = ["graph TD"]
    import_graph = dependencies.get("import_graph", {})
    node_scores = {u: len(v) for u, v in import_graph.items()}
    top_nodes = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)[:15]
    top_node_names = {name for name, _ in top_nodes}

    for u, neighbors in import_graph.items():
        if u in top_node_names:
            u_short = u.split("/")[-1].replace(".py", "")
            for v in neighbors:
                v_short = v.split(".")[-1]
                if any(top_name in v for top_name in top_node_names):
                    graph.append(f"    {u_short} --> {v_short}")

    return "\n".join(graph[:30])

def generate_project_summary(analyses: Dict[str, Any], output_path: pathlib.Path, project_name: str) -> None:
    """Genera resumen ejecutivo del proyecto."""
    structure = analyses.get("structure", {})
    complexity = analyses.get("complexity", {})
    metrics = analyses.get("metrics", {})
    dependencies = analyses.get("dependencies", {})

    summary_content = f"""# RESUMEN DEL PROYECTO - {project_name}
Fecha de análisis: {time.strftime("%Y-%m-%d %H:%M:%S")}
Versión del analizador: 2.0 (Ai-Context-Core)

## 📊 MÉTRICAS CLAVE
- **Total módulos**: {complexity.get("total_modules", 0):,}
- **Líneas de código**: {complexity.get("total_lines", 0):,}
- **Tamaño total**: {structure.get("size_stats", {}).get("total_size_mb", 0):.1f} MB
- **Complejidad promedio**: {complexity.get("average_complexity", 0):.1f}
- **Cobertura de docstrings**: {metrics.get("docstring_coverage", 0):.1f}%
- **Score de calidad**: {metrics.get("quality_score", 0):.1f}/100
- **Archivos de test**: {metrics.get("test_files_count", 0)}

## 📁 ESTRUCTURA
- **Archivos Python**: {structure.get("size_stats", {}).get("python_files", 0)}
- **Total archivos**: {structure.get("size_stats", {}).get("total_files", 0)}
- **Tipo de archivos principales**: {", ".join(list(structure.get("file_types", {}).keys())[:5])}

## 🚨 PROBLEMAS CRÍTICOS
"""

    # Agregar problemas de seguridad
    security = analyses.get("security", [])
    if security:
        summary_content += "\n### 🔒 Problemas de Seguridad:\n"
        high_security = [s for s in security if s.get("max_severity") == "alta"]
        for item in high_security[:3]:
            summary_content += (
                f"- **{item['module']}**: {item['total_issues']} problemas críticos\n"
            )

    # Agregar deuda técnica
    debt = analyses.get("debt", [])
    if debt:
        summary_content += "\n### 🏗️ Deuda Técnica Crítica:\n"
        high_debt = [d for d in debt if d.get("severity_score", 0) >= 5]
        for item in high_debt[:5]:
            summary_content += f"- **{item['module']}**: {item['total_issues']} issues (score: {item['severity_score']})\n"

    # Agregar dependencias circulares
    circular = dependencies.get("circular_dependencies", [])
    if circular:
        summary_content += "\n### 🔄 Dependencias Circulares:\n"
        for cycle in circular[:3]:
            summary_content += f"- {cycle}\n"

    # Agregar cumplimiento QGIS
    qgis = analyses.get("qgis_compliance", {})
    if qgis:
        summary_content += "\n## 📦 ESTÁNDARES DE PLUGIN QGIS\n"
        summary_content += (
            f"- **Score de Cumplimiento**: {qgis.get('compliance_score', 0):.1f}/100\n"
        )

        # Archivos faltantes
        mandatory = qgis.get("mandatory_files", {})
        missing = [f for f, exists in mandatory.get("files", {}).items() if not exists]
        if missing:
            summary_content += f"- ❌ **Archivos faltantes**: {', '.join(missing)}\n"

        # Violaciones de arquitectura
        arch = qgis.get("architecture", {})
        if arch.get("violations"):
            violations = arch["violations"]
            summary_content += f"- ⚠️ **Arquitectura**: {len(violations)} violaciones detectadas (mezcla UI/Core)\n"
            for v in violations[:2]:
                summary_content += f"  - {v['file']}: {v['type']}\n"

        # Recomendaciones de widgets
        widgets = qgis.get("widgets", {})
        if widgets.get("recommendations"):
            summary_content += f"- 💡 **Mejora UI**: {len(widgets['recommendations'])} componentes genéricos podrían ser widgets de QGIS\n"

        # Performance
        perf = qgis.get("performance", {})
        if perf.get("issues"):
            summary_content += f"- ⚡ **Optimización**: {len(perf['issues'])} patrones de rendimiento PyQGIS detectados\n"

    # Agregar recomendaciones
    optimizations = analyses.get("optimizations", [])
    if optimizations:
        summary_content += "\n## 💡 RECOMENDACIONES PRINCIPALES\n"
        high_priority = [o for o in optimizations if o.get("priority") == "alta"]
        for opt in high_priority[:3]:
            summary_content += f"\n### {opt['module']}\n"
            for suggestion in opt["suggestions"][:2]:
                summary_content += f"- {suggestion['message']}\n"

    summary_content += "\n## 📈 DISTRIBUCIÓN DE COMPLEJIDAD\n"
    dist = complexity.get("complexity_distribution", {})
    for key, value in dist.items():
        percentage = (value / complexity.get("total_modules", 1)) * 100
        summary_content += f"- {key}: {value} módulos ({percentage:.1f}%)\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_content)

def generate_ai_context(analyses: Dict[str, Any], output_path: pathlib.Path, project_name: str) -> None:
    """Genera contexto optimizado para IA."""
    structure = analyses.get("structure", {})
    entry_points = analyses.get("entry_points", [])
    patterns = analyses.get("patterns", {})
    complexity = analyses.get("complexity", {})
    dependencies = analyses.get("dependencies", {})

    extra_eps = f"\n... y {len(entry_points) - 10} más" if len(entry_points) > 10 else ""
    context_content = f"""# CONTEXTO PARA IA - {project_name}
Generado automáticamente por Ai-Context-Core
## 📁 ESTRUCTURA DEL PROYECTO

{structure.get("tree", "No disponible")[:1200]}


## 🎯 PUNTOS DE ENTRADA
{chr(10).join(f"- `{ep}`" for ep in entry_points[:10])}
{extra_eps}

## 🏗️ PATRONES DETECTADOS
"""

    # Listar patrones encontrados
    detected_patterns = []
    for pattern_name, pattern_data in patterns.items():
        if isinstance(pattern_data, dict) and pattern_data.get("detected"):
            confidence = pattern_data.get("confidence", 0)
            detected_patterns.append(
                f"- **{pattern_name.upper()}**: Detectado (confianza: {confidence:.0%})"
            )

    if detected_patterns:
        context_content += "\n".join(detected_patterns)
    else:
        context_content += "\nNo se detectaron patrones de diseño claros."

    context_content += f"""
## 📈 COMPLEJIDAD Y MÉTRICAS
- **Módulos totales**: {complexity.get("total_modules", 0)}
- **Líneas de código**: {complexity.get("total_lines", 0):,}
- **Funciones**: {complexity.get("total_functions", 0)}
- **Clases**: {complexity.get("total_classes", 0)}
- **Complejidad promedio**: {complexity.get("average_complexity", 0):.1f}
- **Módulos más complejos**: {", ".join([m[0] for m in complexity.get("most_complex_modules", [])[:3]])}

## 🔗 DEPENDENCIAS PRINCIPALES
"""

    # Agregar dependencias principales
    third_party = dependencies.get("third_party", [])
    if third_party:
        # Agrupar por paquete base
        base_packages = {}
        for dep in third_party:
            base = dep.split(".")[0]
            base_packages[base] = base_packages.get(base, 0) + 1

        context_content += "\n### Third Party (más frecuentes):\n"
        for package, count in sorted(base_packages.items(), key=lambda x: x[1], reverse=True)[
            :15
        ]:
            context_content += f"- `{package}` ({count} imports)\n"

    # Agregar recomendaciones principales
    optimizations = analyses.get("optimizations", [])
    if optimizations:
        context_content += "\n## 💡 RECOMENDACIONES DE OPTIMIZACIÓN\n"
        for opt in optimizations[:5]:
            context_content += f"\n### {opt['module']} (Prioridad: {opt['priority'].upper()})\n"
            for suggestion in opt["suggestions"][:2]:
                context_content += f"- **{suggestion['type']}**: {suggestion['message']}\n"

    # Agregar estructura de dependencias
    graph_metrics = dependencies.get("graph_metrics", {})
    if graph_metrics:
        context_content += f"""
## 🕸️  ESTRUCTURA DE DEPENDENCIAS
- **Nodos**: {graph_metrics.get("nodes", 0)}
- **Aristas**: {graph_metrics.get("edges", 0)}
- **Densidad**: {graph_metrics.get("density", 0):.3f}
- **Grafo acíclico**: {"Sí" if graph_metrics.get("is_dag", False) else "No"}
- **Componentes conectados**: {graph_metrics.get("weakly_connected_components", 0)}

## 🕸️ DIAGRAMA DE DEPENDENCIAS (Conceptuall)
```mermaid
{generate_mermaid_graph(dependencies)}
```

## 🔑 PALABRAS CLAVE DEL PROYECTO
"""
    # Por ahora, un resumen de los tipos de archivos y patterns detectados
    context_content += (
        "- **Tecnologías**: "
        + ", ".join(list(structure.get("file_types", {}).keys())[:8])
        + "\n"
    )
    context_content += (
        "- **Patrones**: "
        + ", ".join(
            [p for p, d in patterns.items() if isinstance(d, dict) and d.get("detected")]
        )
        + "\n"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(context_content)
