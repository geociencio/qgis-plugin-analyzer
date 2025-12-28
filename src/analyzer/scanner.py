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

import ast
import re
import pathlib
from typing import Any, Dict, List, Optional

def get_qgis_audit_rules() -> List[Dict[str, Any]]:
    """Devuelve el catálogo de reglas de auditoría de QGIS."""
    return [
        {
            "id": "OBSOLETE_API",
            "pattern": r"writeAsVectorFormat\(",
            "message": "Uso de writeAsVectorFormat() obsoleto. Usar writeAsVectorFormatV3().",
            "severity": "alta",
        },
        {
            "id": "UNPRECISE_LAYER_LOOKUP",
            "pattern": r"mapLayersByName\(",
            "message": "mapLayersByName() puede ser impreciso. Considerar mapLayers() o IDs únicos.",
            "severity": "media",
        },
        {
            "id": "MISSING_I18N",
            "pattern": r"\.(?:setText|setWindowTitle|setTitle|setToolTip|setPlaceholderText|setTabText)\(\s*['\"](?![%])",
            "message": "Cadena de texto en UI sin traducir. Usar self.tr().",
            "severity": "alta",
        },
        {
            "id": "UNSAFE_THREADING",
            "pattern": r"\bthreading\.Thread\(",
            "message": "Uso de threading.Thread detectado. Preferir QgsTask o QThread.",
            "severity": "alta",
        },
        {
            "id": "MANUAL_RESOURCE_PATH",
            "pattern": r"QIcon\(\s*['\"](?!\s*:\/)[^'\"]*?(?:icons|images|ui)/",
            "message": "Ruta de recurso manual detectada. Usar :/plugins/...",
            "severity": "media",
        },
        {
            "id": "PRINT_STATEMENT",
            "pattern": r"^[^#]*\bprint\(",
            "message": "Uso de print() detectado. Usar QgsMessageLog.",
            "severity": "baja",
        },
    ]

def analyze_module_worker(py_file: pathlib.Path, project_path: pathlib.Path, cached_data: Optional[Dict] = None) -> Optional[Dict]:
    """Trabajador para análisis de módulo (ejecutado en subprocesos)."""
    try:
        rel_path = str(py_file.relative_to(project_path))
        
        # Lectura rápida
        with open(py_file, "r", encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
        
        if not content:
            return None

        # Parsear AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {
                "path": rel_path,
                "lines": content.count("\n") + 1,
                "syntax_error": True,
                "file_size_kb": py_file.stat().st_size / 1024,
            }

        # Extracción de info
        functions = []
        classes = []
        imports = []
        complexity = 1
        has_main = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(f"{node.name}({len(node.args.args)} args)")
            elif isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b) for b in node.bases]
                classes.append(f"{node.name}({', '.join(bases)})" if bases else node.name)
            elif isinstance(node, ast.Import):
                imports.extend(n.name for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler)):
                complexity += 1
            
            # Check main guard
            if isinstance(node, ast.If) and not has_main:
                if isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name):
                    if node.test.left.id == "__name__":
                        for cmp in node.test.comparators:
                            if isinstance(cmp, ast.Constant) and cmp.value == "__main__":
                                has_main = True

        return {
            "path": rel_path,
            "lines": content.count("\n") + 1,
            "functions": functions,
            "classes": classes,
            "imports": sorted(set(imports)),
            "complexity": complexity,
            "has_main": has_main,
            "docstrings": {
                "module": ast.get_docstring(tree) is not None,
            },
            "file_size_kb": py_file.stat().st_size / 1024,
            "syntax_error": False,
        }
    except Exception:
        return None

def audit_qgis_standards(modules_data: List[Dict], project_path: pathlib.Path) -> Dict[str, Any]:
    """Ejecuta la auditoría de estándares QGIS basada en regex."""
    rules = get_qgis_audit_rules()
    results = {"issues": [], "issues_count": 0}
    
    for module in modules_data:
        path = module.get("path")
        if not path: continue
        
        full_path = project_path / path
        if not full_path.exists(): continue
        
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            for rule in rules:
                for match in re.finditer(rule["pattern"], content, re.MULTILINE):
                    line_no = content.count("\n", 0, match.start()) + 1
                    results["issues"].append({
                        "file": path,
                        "line": line_no,
                        "type": rule["id"],
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "code": content[match.start():match.end()+20].strip()
                    })
        except Exception:
            continue
            
    results["issues_count"] = len(results["issues"])
    return results

def validate_plugin_structure(project_path: pathlib.Path) -> Dict[str, Any]:
    """Verifica la presencia de archivos obligatorios."""
    mandatory = ["metadata.txt", "__init__.py", "LICENSE"]
    found = {f: (project_path / f).exists() for f in mandatory}
    
    # Verificar classFactory en __init__.py
    init_file = project_path / "__init__.py"
    has_factory = False
    if init_file.exists():
        has_factory = "def classFactory" in init_file.read_text(encoding="utf-8", errors="replace")
        
    return {
        "files": found,
        "has_class_factory": has_factory,
        "is_valid": all(found.values()) and has_factory
    }

def validate_metadata(project_path: pathlib.Path) -> Dict[str, Any]:
    """Valida el contenido de metadata.txt."""
    metadata_path = project_path / "metadata.txt"
    required = ["name", "description", "version", "qgisMinimumVersion", "author", "email"]
    
    if not metadata_path.exists():
        return {"is_valid": False, "missing": required}
        
    content = metadata_path.read_text(encoding="utf-8", errors="replace").lower()
    missing = [f for f in required if f.lower() + "=" not in content]
    
    return {
        "is_valid": len(missing) == 0,
        "missing": missing,
        "fields_found": [f for f in required if f not in missing]
    }
