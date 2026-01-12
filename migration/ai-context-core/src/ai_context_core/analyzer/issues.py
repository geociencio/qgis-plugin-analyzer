
from typing import List, Dict, Any, Tuple
import re
from pathlib import Path

def find_technical_debt(modules_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identifica deuda técnica con severidad."""
    debt_items = []

    for module in modules_data:
        path = module.get("path", "")
        complexity = module.get("complexity", 0)
        lines = module.get("lines", 0)
        docstrings = module.get("docstrings", {})

        issues = []

        # Clasificar por severidad
        if complexity > 20:
            issues.append(
                {
                    "type": "alta_complejidad",
                    "severity": "alta",
                    "message": f"Complejidad ciclomática muy alta ({complexity})",
                    "value": complexity,
                }
            )
        elif complexity > 10:
            issues.append(
                {
                    "type": "complejidad_moderada",
                    "severity": "media",
                    "message": f"Complejidad ciclomática alta ({complexity})",
                    "value": complexity,
                }
            )

        if lines > 800:
            issues.append(
                {
                    "type": "archivo_muy_largo",
                    "severity": "alta",
                    "message": f"Archivo muy largo ({lines} líneas)",
                    "value": lines,
                }
            )
        elif lines > 500:
            issues.append(
                {
                    "type": "archivo_largo",
                    "severity": "media",
                    "message": f"Archivo largo ({lines} líneas)",
                    "value": lines,
                }
            )

        if not docstrings.get("module", False):
            issues.append(
                {
                    "type": "sin_docstring_modulo",
                    "severity": "baja",
                    "message": "Falta docstring a nivel de módulo",
                }
            )

        # Verificar docstrings en clases y funciones
        classes_without_doc = sum(
            1 for has_doc in docstrings.get("classes", {}).values() if not has_doc
        )
        funcs_without_doc = sum(
            1 for has_doc in docstrings.get("functions", {}).values() if not has_doc
        )

        if classes_without_doc > 0:
            issues.append(
                {
                    "type": "clases_sin_docstring",
                    "severity": "baja",
                    "message": f"{classes_without_doc} clases sin docstring",
                }
            )

        if funcs_without_doc > 0:
            issues.append(
                {
                    "type": "funciones_sin_docstring",
                    "severity": "baja",
                    "message": f"{funcs_without_doc} funciones sin docstring",
                }
            )

        if issues:
            debt_items.append(
                {
                    "module": path,
                    "issues": issues,
                    "total_issues": len(issues),
                    "severity_score": sum(
                        3 if i["severity"] == "alta" else 2 if i["severity"] == "media" else 1
                        for i in issues
                    ),
                }
            )

    # Ordenar por severidad
    debt_items.sort(key=lambda x: x["severity_score"], reverse=True)
    return debt_items[:50]  # Limitar resultados

def find_optimizations(modules_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identifica oportunidades de optimización específicas."""
    optimizations = []

    for module in modules_data:
        path = module.get("path", "")
        imports = module.get("imports", [])
        complexity = module.get("complexity", 0)
        functions = module.get("functions", [])
        lines = module.get("lines", 0)

        suggestions = []

        # Optimizaciones basadas en imports
        if len(imports) > 25:
            suggestions.append(
                {
                    "type": "imports_excesivos",
                    "priority": "media",
                    "message": f"Muchos imports ({len(imports)})",
                    "suggestions": [
                        "Agrupar imports relacionados",
                        "Usar imports locales dentro de funciones",
                        "Eliminar imports no utilizados con herramientas como autoflake",
                    ],
                }
            )

        # Optimizaciones de complejidad
        if complexity > 15 and len(functions) > 5:
            suggestions.append(
                {
                    "type": "refactorizacion_complejidad",
                    "priority": "alta",
                    "message": f"Alta complejidad ({complexity}) con {len(functions)} funciones",
                    "suggestions": [
                        "Extraer métodos de funciones largas",
                        "Usar polimorfismo en lugar de if/else largos",
                        "Aplicar principios SOLID",
                        "Considerar usar patrones de diseño",
                    ],
                }
            )

        # Optimizaciones de tamaño
        if lines > 300:
            suggestions.append(
                {
                    "type": "modulo_demasiado_grande",
                    "priority": "media",
                    "message": f"Módulo muy grande ({lines} líneas)",
                    "suggestions": [
                        "Dividir en múltiples módulos",
                        "Agrupar funcionalidad relacionada en paquetes",
                        "Extraer clases a módulos separados",
                    ],
                }
            )

        # Detectar funciones demasiado largas
        if functions and lines / len(functions) > 50:
            suggestions.append(
                {
                    "type": "funciones_demasiado_largas",
                    "priority": "media",
                    "message": f"Funciones muy largas (promedio {lines / len(functions):.1f} líneas/función)",
                    "suggestions": [
                        "Refactorizar funciones > 50 líneas",
                        "Extraer lógica común a funciones helper",
                        "Usar comprehensions y generadores",
                    ],
                }
            )

        if suggestions:
            optimizations.append(
                {
                    "module": path,
                    "suggestions": suggestions,
                    "priority": "alta" if complexity > 20 else "media",
                }
            )

    return optimizations[:30]  # Limitar resultados

def find_security_issues(modules_data: List[Dict[str, Any]], project_path: str) -> List[Dict[str, Any]]:
    """Identifica posibles problemas de seguridad."""
    security_issues = []
    base_path = Path(project_path)

    dangerous_patterns = [
        ("exec(", "Uso de exec() - Vulnerable a inyección de código", "alta"),
        ("eval(", "Uso de eval() - Vulnerable a inyección de código", "alta"),
        ("pickle.loads", "Deserialización insegura - Puede ejecutar código arbitrario", "alta"),
        ("subprocess.call(", "Ejecución de shell sin sanitizar", "alta"),
        ("subprocess.Popen(", "Ejecución de shell sin sanitizar", "alta"),
        ("os.system(", "Ejecución de comandos del sistema", "alta"),
        ("input()", "Entrada de usuario sin validar", "media"),
        ("open(", "Apertura de archivos sin validar ruta", "media"),
        ("yaml.load(", "Carga de YAML insegura (usar yaml.safe_load)", "alta"),
        ("marshal.loads", "Deserialización insegura", "alta"),
        ("sqlite3.execute(", "Posible inyección SQL (usar parámetros)", "alta"),
        ("flask.request.args.get", "Parámetros GET sin validar", "media"),
        ("django.forms.CharField", "Validación insuficiente", "media"),
        ("md5(", "Uso de hash MD5 inseguro", "media"),
        ("sha1(", "Uso de hash SHA1 inseguro", "media"),
    ]

    for module in modules_data:
        path = module.get("path", "")
        if not path:
            continue

        try:
            full_path = base_path / path
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except:
            continue

        issues_found = []
        for pattern, description, severity in dangerous_patterns:
            if pattern in content:
                # Encontrar línea específica
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if pattern in line and not line.strip().startswith("#"):
                        issues_found.append(
                            {
                                "pattern": pattern,
                                "description": description,
                                "severity": severity,
                                "line": i,
                                "code": line.strip()[:120],
                            }
                        )
                        break  # Solo primera ocurrencia por patrón

        if issues_found:
            security_issues.append(
                {
                    "module": path,
                    "issues": issues_found,
                    "total_issues": len(issues_found),
                    "max_severity": max(
                        (i["severity"] for i in issues_found),
                        key=lambda x: {"alta": 3, "media": 2, "baja": 1}[x],
                    ),
                }
            )

    # Ordenar por severidad
    security_issues.sort(
        key=lambda x: {"alta": 3, "media": 2, "baja": 1}[x["max_severity"]], reverse=True
    )
    return security_issues[:20]  # Limitar resultados
