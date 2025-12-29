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
    """Returns the QGIS audit rule catalog."""
    return [
        {
            "id": "UNPRECISE_LAYER_LOOKUP",
            "pattern": r"mapLayersByName\(",
            "message": "mapLayersByName() can be imprecise. Consider mapLayers() or unique IDs.",
            "severity": "medium",
        },
        {
            "id": "UNSAFE_THREADING",
            "pattern": r"\bthreading\.Thread\(",
            "message": "threading.Thread usage detected. Prefer QgsTask or QThread.",
            "severity": "high",
        },
        {
            "id": "MANUAL_RESOURCE_PATH",
            "pattern": r"QIcon\(\s*['\"](?!\s*:\/)[^'\"]*?(?:icons|images|ui)/",
            "message": "Manual resource path detected. Use :/plugins/...",
            "severity": "medium",
        },
        {
            "id": "PRINT_STATEMENT",
            "pattern": r"^[^#]*\bprint\(",
            "message": "print() usage detected. Use QgsMessageLog.",
            "severity": "low",
        },
    ]

class QGISASTVisitor(ast.NodeVisitor):
    """AST visitor to detect QGIS-specific issues."""
    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.issues = []
        self.i18n_methods = {
            "setText", "setWindowTitle", "setTitle", "setToolTip", 
            "setPlaceholderText", "setTabText"
        }

    def visit_Call(self, node: ast.Call):
        # 1. Detect OBSOLETE_API (writeAsVectorFormat)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "writeAsVectorFormat":
            self.issues.append({
                "file": self.rel_path,
                "line": node.lineno,
                "type": "OBSOLETE_API",
                "severity": "high",
                "message": "Obsolete writeAsVectorFormat() usage. Use writeAsVectorFormatV3().",
                "code": ast.unparse(node)
            })

        # 2. Detect MISSING_I18N
        if isinstance(node.func, ast.Attribute) and node.func.attr in self.i18n_methods:
            # Check if the first argument is a literal string and NOT wrapped in self.tr() or similar
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                val = node.args[0].value
                # Ignore empty strings or strings starting with % (placeholders)
                if val.strip() and not val.startswith("%"):
                    self.issues.append({
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "MISSING_I18N",
                        "severity": "high",
                        "message": f"Untranslated UI text string in '{node.func.attr}': '{val}'. Use self.tr().",
                        "code": ast.unparse(node)
                    })

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        # 3. Detect MANDATORY_CLEANUP
        # Simple check: if a class has initGui, it MUST have unload
        has_init_gui = any(isinstance(m, ast.FunctionDef) and m.name == "initGui" for m in node.body)
        has_unload = any(isinstance(m, ast.FunctionDef) and m.name == "unload" for m in node.body)
        
        if has_init_gui and not has_unload:
            self.issues.append({
                "file": self.rel_path,
                "line": node.lineno,
                "type": "MANDATORY_CLEANUP",
                "severity": "high",
                "message": f"Class '{node.name}' implements 'initGui()' but is missing 'unload()'. Mandatory for cleanup.",
                "code": f"class {node.name}..."
            })
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # 4. Detect IFACE_AS_ARGUMENT (QGS105)
        # Avoid passing QgisInterface as an argument
        for arg in node.args.args:
            if arg.annotation and isinstance(arg.annotation, ast.Name):
                if arg.annotation.id == "QgisInterface":
                    self.issues.append({
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "IFACE_AS_ARGUMENT",
                        "severity": "medium",
                        "message": f"Function '{node.name}' receives 'QgisInterface' as an argument. Use the global 'iface' or Singleton pattern.",
                        "code": ast.unparse(node).split("\n")[0]
                    })
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            # 5. Detect QGIS_PROTECTED_MEMBER (QGS101/102)
            if alias.name.startswith("qgis._") and not alias.name.startswith("qgis._3d"):
                 self.issues.append({
                    "file": self.rel_path,
                    "line": node.lineno,
                    "type": "QGIS_PROTECTED_MEMBER",
                    "severity": "high",
                    "message": f"Protected member import detected: '{alias.name}'. Protected members are unstable.",
                    "code": ast.unparse(node)
                })
            # 6. Detect GDAL_DIRECT_IMPORT (QGS106)
            if alias.name == "gdal":
                self.issues.append({
                    "file": self.rel_path,
                    "line": node.lineno,
                    "type": "GDAL_DIRECT_IMPORT",
                    "severity": "medium",
                    "message": "Direct 'gdal' import detected. Use 'from osgeo import gdal'.",
                    "code": ast.unparse(node)
                })
            # QGIS_LEGACY_IMPORT (already existing)
            if alias.name.startswith(("PyQt4", "PyQt5")):
                self.issues.append({
                    "file": self.rel_path,
                    "line": node.lineno,
                    "type": "QGIS_LEGACY_IMPORT",
                    "severity": "high",
                    "message": f"Legacy import detected: '{alias.name}'. Use 'qgis.PyQt' for compatibility.",
                    "code": ast.unparse(node)
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            # Detect QGIS_PROTECTED_MEMBER
            if node.module.startswith("qgis._") and not node.module.startswith("qgis._3d"):
                self.issues.append({
                    "file": self.rel_path,
                    "line": node.lineno,
                    "type": "QGIS_PROTECTED_MEMBER",
                    "severity": "high",
                    "message": f"Protected member import detected: 'from {node.module} import ...'. Protected members are unstable.",
                    "code": ast.unparse(node)
                })
            # Detect GDAL_DIRECT_IMPORT
            if node.module == "gdal":
                self.issues.append({
                    "file": self.rel_path,
                    "line": node.lineno,
                    "type": "GDAL_DIRECT_IMPORT",
                    "severity": "medium",
                    "message": "Direct 'gdal' import detected. Use 'from osgeo import gdal'.",
                    "code": ast.unparse(node)
                })
            # QGIS_LEGACY_IMPORT
            if node.module.startswith(("PyQt4", "PyQt5")):
                self.issues.append({
                    "file": self.rel_path,
                    "line": node.lineno,
                    "type": "QGIS_LEGACY_IMPORT",
                    "severity": "high",
                    "message": f"Legacy import detected: 'from {node.module} import ...'. Use 'qgis.PyQt' for compatibility.",
                    "code": ast.unparse(node)
                })
        self.generic_visit(node)

def analyze_module_worker(py_file: pathlib.Path, project_path: pathlib.Path, cached_data: Optional[Dict] = None) -> Optional[Dict]:
    """Worker for module analysis (executed in sub-processes)."""
    try:
        rel_path = str(py_file.relative_to(project_path))
        
        # Fast read
        with open(py_file, "r", encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
        
        if not content:
            return None

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {
                "path": rel_path,
                "lines": content.count("\n") + 1,
                "syntax_error": True,
                "file_size_kb": py_file.stat().st_size / 1024,
            }

        # Info extraction
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

        # Custom AST Audit
        visitor = QGISASTVisitor(rel_path)
        visitor.visit(tree)

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
            "ast_issues": visitor.issues
        }
    except Exception:
        return None

def audit_qgis_standards(modules_data: List[Dict], project_path: pathlib.Path) -> Dict[str, Any]:
    """Executes regex-based QGIS standards audit."""
    rules = get_qgis_audit_rules()
    results = {"issues": [], "issues_count": 0}
    
    for module in modules_data:
        # Add issues found via AST
        if "ast_issues" in module:
            results["issues"].extend(module["ast_issues"])

        path = module.get("path")
        if not path:
            continue
        
        full_path = project_path / path
        if not full_path.exists():
            continue
        
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
    """Verifies presence of mandatory files."""
    mandatory = ["metadata.txt", "__init__.py", "LICENSE"]
    found = {f: (project_path / f).exists() for f in mandatory}
    
    # Check classFactory in __init__.py
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
    """Validates metadata.txt content."""
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
