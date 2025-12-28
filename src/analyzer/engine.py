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

import os
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from .scanner import analyze_module_worker, audit_qgis_standards, validate_plugin_structure, validate_metadata
from .utils import ProgressTracker, LRUCache
from .reporters import generate_markdown_summary, save_json_context

class ProjectAnalyzer:
    def __init__(self, project_path: str, output_dir: Optional[str] = None):
        self.project_path = pathlib.Path(project_path).resolve()
        self.output_dir = pathlib.Path(output_dir or "./analysis_results").resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = os.cpu_count() or 4
        
    def get_python_files(self) -> List[pathlib.Path]:
        """Escanea archivos Python ignorando carpetas comunes."""
        exclude = {"venv", ".venv", "__pycache__", ".git", "build", "dist"}
        python_files = []
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in exclude]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(pathlib.Path(root) / file)
        return sorted(python_files)

    def run(self):
        """Ejecuta el pipeline de análisis."""
        print(f"🔍 Analizando: {self.project_path}")
        files = self.get_python_files()
        tracker = ProgressTracker(len(files))
        modules_data = []

        # Análisis en paralelo
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(analyze_module_worker, f, self.project_path): f for f in files}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    modules_data.append(res)
                tracker.update(futures[future], 0)

        # Análisis de cumplimiento QGIS
        compliance = audit_qgis_standards(modules_data, self.project_path)
        
        # Auditoría de repositorio oficial
        structure = validate_plugin_structure(self.project_path)
        metadata = validate_metadata(self.project_path)

        # Calcular métricas básicas
        code_score, qgis_score = self._calculate_scores(modules_data, compliance, structure, metadata)
        
        metrics = {
            "total_files": len(files),
            "total_lines": sum(m["lines"] for m in modules_data),
            "quality_score": round((code_score * 0.5) + (qgis_score * 0.5), 1)
        }

        analyses = {
            "project_name": self.project_path.name,
            "metrics": metrics,
            "qgis_compliance": {
                "compliance_score": round(qgis_score, 1),
                "best_practices": compliance,
                "repository_standards": {
                    "structure": structure,
                    "metadata": metadata
                }
            },
            "modules": modules_data
        }

        # Guardar reportes
        generate_markdown_summary(analyses, self.output_dir / "PROJECT_SUMMARY.md")
        save_json_context(analyses, self.output_dir / "project_context.json")
        
        tracker.complete()
        print(f"✅ Análisis completado. Reportes en: {self.output_dir}")

    def _calculate_scores(self, modules_data, compliance, structure, metadata) -> tuple:
        """Cálculo de scores basado en estándares QGIS y calidad de código."""
        if not modules_data: return 0.0, 0.0
        
        # 1. Base Calidad de Código (50%)
        avg_comp = sum(m["complexity"] for m in modules_data) / len(modules_data)
        code_score = max(0, 100 - (avg_comp * 3))
        
        # 2. Estándares QGIS (50%)
        qgis_score = 100
        # Penalización por hallazgos técnicos
        qgis_score -= compliance.get("issues_count", 0) * 2
        # Penalización por faltas de repositorio
        if not structure["is_valid"]: qgis_score -= 20
        if not metadata["is_valid"]: qgis_score -= 10
        
        return code_score, max(0, qgis_score)
