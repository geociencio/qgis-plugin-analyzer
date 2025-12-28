# /***************************************************************************
#  QGIS Plugin Analyzer
#                                  A QGIS tool
#  Static code analysis and standards audit for QGIS plugins.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import json
import datetime
import pathlib
from typing import Any, Dict

def generate_markdown_summary(analyses: Dict[str, Any], output_path: pathlib.Path):
    """Genera un reporte PROJECT_SUMMARY.md profesional."""
    metrics = analyses.get("metrics", {})
    compliance = analyses.get("qgis_compliance", {})
    score = metrics.get("quality_score", 0)
    qgis_score = compliance.get("compliance_score", 0)
    
    lines = [
        f"# 📋 Informe de Análisis de Proyecto: {analyses.get('project_name', 'QGIS Plugin')}",
        f"*Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## 📊 Indicadores de Calidad",
        f"- **Puntuación de Código**: `{score}/100`",
        f"- **Cumplimiento QGIS**: `{qgis_score}/100`",
        "",
    ]
    # Hallazgos técnicos
    best_practices = compliance.get("best_practices", {})
    lines.append(f"## 🛠️ Hallazgos de Estándares QGIS")
    lines.append(f"Se detectaron **{best_practices.get('issues_count', 0)}** desviaciones técnicas.")
    
    for issue in best_practices.get("issues", []):
        icon = "🔴" if issue["severity"] == "alta" else "🟡"
        lines.append(f"- {icon} `{issue['file']}:{issue['line']}`: {issue['message']}")
        
    # Auditoría de Repositorio
    repo_stats = compliance.get("repository_standards", {})
    lines.append("\n## 📦 Estándares de Repositorio Oficial")
    
    struct = repo_stats.get("structure", {})
    status = "✅ OK" if struct.get("is_valid") else "❌ Incompleto"
    lines.append(f"- **Estructura de Archivos**: {status}")
    if not struct.get("is_valid"):
        missing_files = [f for f, found in struct.get("files", {}).items() if not found]
        if missing_files: lines.append(f"  - Faltan: `{', '.join(missing_files)}`")
        if not struct.get("has_class_factory"): lines.append("  - Falta `classFactory` en `__init__.py`")

    meta = repo_stats.get("metadata", {})
    status_meta = "✅ OK" if meta.get("is_valid") else "🛠️ Requiere Atención"
    lines.append(f"- **Metadatos (metadata.txt)**: {status_meta}")
    if not meta.get("is_valid"):
        lines.append(f"  - Campos faltantes: `{', '.join(meta.get('missing', []))}`")

    lines.append("\n## 📈 Métricas Generales")
    for k, v in metrics.items():
        if k != "quality_score":
            lines.append(f"- **{k.replace('_', ' ').title()}**: {v}")
            
    output_path.write_text("\n".join(lines), encoding="utf-8")

def save_json_context(analyses: Dict[str, Any], output_path: pathlib.Path):
    """Guarda el contexto completo en JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analyses, f, indent=2, ensure_ascii=False)
