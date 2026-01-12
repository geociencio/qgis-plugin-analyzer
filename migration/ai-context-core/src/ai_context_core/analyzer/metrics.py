
from typing import List, Dict, Any

def calculate_complexity_distribution(modules_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calcula distribución de complejidad."""
    distribution = {"low (0-5)": 0, "medium (6-15)": 0, "high (16-30)": 0, "very_high (31+)": 0}

    for module in modules_data:
        complexity = module.get("complexity", 0)
        if complexity <= 5:
            distribution["low (0-5)"] += 1
        elif complexity <= 15:
            distribution["medium (6-15)"] += 1
        elif complexity <= 30:
            distribution["high (16-30)"] += 1
        else:
            distribution["very_high (31+)"] += 1

    return distribution

def calculate_quality_score(modules_data: List[Dict[str, Any]], config: Dict[str, Any], context_patterns: Dict[str, Any]) -> float:
    """Calcula un score de calidad general."""
    if not modules_data:
        return 0.0

    weights = config.get("quality_weights", {})
    thresholds = config.get("thresholds", {})

    # Calcular puntuación máxima posible por módulo
    max_module_score = (
        weights.get("docstrings", 0)
        + weights.get("complexity_low", 0)
        + weights.get("size_small", 0)
        + weights.get("has_main", 0)
        + weights.get("no_syntax_error", 0)
    )

    total_score = 0.0
    max_possible_total = len(modules_data) * max_module_score

    for module in modules_data:
        module_score = 0

        # Puntos por tener docstring
        if module.get("docstrings", {}).get("module", False):
            module_score += weights.get("docstrings", 0)

        # Puntos por complejidad baja
        complexity = module.get("complexity", 0)
        if complexity <= thresholds.get("complexity_low", 5):
            module_score += weights.get("complexity_low", 0)
        elif complexity <= thresholds.get("complexity_medium", 10):
            module_score += weights.get("complexity_medium", 0)
        elif complexity <= thresholds.get("complexity_high", 15):
            module_score += weights.get("complexity_high", 0)

        # Puntos por tamaño adecuado
        lines = module.get("lines", 0)
        if lines <= thresholds.get("size_small", 200):
            module_score += weights.get("size_small", 0)
        elif lines <= thresholds.get("size_medium", 400):
            module_score += weights.get("size_medium", 0)

        # Puntos por tener main guard
        if module.get("has_main", False):
            module_score += weights.get("has_main", 0)

        # Puntos por no tener errores de sintaxis
        if not module.get("syntax_error", False):
            module_score += weights.get("no_syntax_error", 0)

        total_score += module_score

    # Normalizar a porcentaje
    final_score = (total_score / max_possible_total) * 100 if max_possible_total > 0 else 0

    # Factorizar el score de cumplimiento de QGIS (si existe)
    qgis_data = context_patterns.get("qgis_compliance", {})
    qgis_score = qgis_data.get("compliance_score")

    if qgis_score is not None:
        # El Score final es un promedio ponderada: 60% Calidad Código, 30% Estándares QGIS, 10% Linter
        final_score = (final_score * 0.7) + (qgis_score * 0.3)

    # Penalización por errores de linter
    linter_data = context_patterns.get("linter", {})
    if linter_data.get("available"):
        errors = linter_data.get("errors", 0)
        # Penalizar 0.5 puntos por error, máx 10 puntos
        penalty = min(10, errors * 0.5)
        final_score = max(0, final_score - penalty)

    return round(final_score, 1)

def calculate_project_metrics(modules_data: List[Dict[str, Any]], context_entry_points: List[str], test_files_count: int, config: Dict[str, Any], context_patterns: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula métricas generales del proyecto."""
    if not modules_data:
        return {}

    total_size_kb = sum(m.get("file_size_kb", 0) for m in modules_data)
    total_lines = sum(m.get("lines", 0) for m in modules_data)

    # Calcular métricas de calidad
    modules_with_docstrings = sum(
        1 for m in modules_data if m.get("docstrings", {}).get("module", False)
    )

    modules_with_main = sum(1 for m in modules_data if m.get("has_main", False))
    modules_with_syntax_error = sum(1 for m in modules_data if m.get("syntax_error", False))

    # Calcular estadísticas de complejidad
    complexities = [m.get("complexity", 0) for m in modules_data]
    avg_complexity = sum(complexities) / len(complexities) if complexities else 0

    # Calcular promedios de nuevas métricas
    type_hint_cov = [m.get("type_hints", {}).get("coverage", 100) for m in modules_data]
    i18n_scores = [m.get("i18n", {}).get("i18n_score", 100) for m in modules_data]

    return {
        "total_size_kb": round(total_size_kb, 2),
        "total_lines_code": total_lines,
        "avg_module_size_kb": round(total_size_kb / len(modules_data), 2),
        "avg_lines_per_module": round(total_lines / len(modules_data), 2),
        "modules_with_docstrings": modules_with_docstrings,
        "modules_with_main_guard": modules_with_main,
        "modules_with_syntax_errors": modules_with_syntax_error,
        "docstring_coverage": round(modules_with_docstrings / len(modules_data) * 100, 2),
        "type_hint_coverage": round(sum(type_hint_cov) / len(modules_data), 2)
        if modules_data
        else 0,
        "i18n_coverage": round(sum(i18n_scores) / len(modules_data), 2) if modules_data else 0,
        "entry_points_count": len(context_entry_points),
        "test_files_count": test_files_count,
        "avg_complexity": round(avg_complexity, 2),
        "max_complexity": max(complexities) if complexities else 0,
        "quality_score": calculate_quality_score(modules_data, config, context_patterns),
    }
