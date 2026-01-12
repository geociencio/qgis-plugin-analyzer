
import logging
import time
import ast
import concurrent.futures
import pathlib
import json
from typing import Dict, Any, List

from . import ast_utils, fs_utils, metrics, issues, reporting, dependencies
from ..context.manager import AIContextManager

logger = logging.getLogger(__name__)

class ProjectAnalyzer:
    """Analizador de proyectos Python optimizado y modular."""

    def __init__(
        self,
        project_path: str,
        config: Dict[str, Any] = None,
        max_workers: int = None,
        exclude_patterns: List[str] = None,
    ):
        self.project_path = pathlib.Path(project_path).resolve()
        self.max_workers = max_workers or (2 * (1 if not hasattr(time, 'get_clock_info') else 4)) # Fallback safe
        self.config = config or {}
        
        # Cargar patrones de exclusión
        self.exclusion_patterns = fs_utils.load_exclusion_patterns(
            self.project_path, exclude_patterns
        )

        # Contexto AI
        self.context_manager = AIContextManager(project_path)
        
        # Cache
        self.ast_cache = {}
        self.file_cache = {}
        
        # Estado
        self.error_log = {}

        # Default Config si no se pasa
        if not self.config:
            self._apply_default_config()

    def _apply_default_config(self):
        """Aplica configuración por defecto."""
        self.config = {
            "quality_weights": {
                "docstrings": 30,
                "complexity_low": 20,
                "size_small": 15,
                "has_main": 5,
                "no_syntax_error": 30,
                "complexity_medium": 10,
                "complexity_high": -10,
                "size_medium": 10,
            },
            "thresholds": {
                "complexity_low": 5,
                "complexity_medium": 15,
                "complexity_high": 25,
                "size_small": 200,
                "size_medium": 500,
            },
        }

    def analyze(self) -> Dict[str, Any]:
        """Ejecuta el análisis completo del proyecto."""
        start_time = time.time()
        logger.info(f"Iniciando análisis de {self.project_path}")

        # 1. Obtener archivos
        python_files = fs_utils.get_python_files_filtered(
            self.project_path, self.exclusion_patterns
        )
        logger.info(f"Encontrados {len(python_files)} archivos Python")

        # 2. Análisis paralelo de módulos
        modules_data = self._analyze_modules_parallel(python_files)

        # 3. Análisis de estructura
        structure = fs_utils.analyze_structure(self.project_path, len(modules_data))

        # 4. Análisis de dependencias
        deps_data = dependencies.analyze_dependencies(
            modules_data, self.project_path, fs_utils.read_file_fast
        )
        
        # 5. Métricas globales
        test_files_count = fs_utils.count_test_files(self.project_path)
        entry_points = [m["path"] for m in modules_data if m.get("has_main")]
        
        project_metrics = metrics.calculate_project_metrics(
            modules_data, 
            entry_points, 
            test_files_count, 
            self.config, 
            {"qgis_compliance": {}} # TODO: Implementar análisis QGIS real
        )
        
        complexity_dist = metrics.calculate_complexity_distribution(modules_data)

        # 6. Detección de problemas y optimizaciones
        tech_debt = issues.find_technical_debt(modules_data)
        optimization_suggestions = issues.find_optimizations(modules_data)
        security_list = issues.find_security_issues(modules_data, str(self.project_path))

        # 7. Ensamblar resultados
        results = {
            "project_name": self.project_path.name,
            "timestamp": time.time(),
            "metrics": project_metrics,
            "structure": structure,
            "complexity": {
                "total_modules": len(modules_data),
                "total_lines": project_metrics.get("total_lines_code", 0),
                "total_functions": sum(len(m.get("functions", [])) for m in modules_data),
                "total_classes": sum(len(m.get("classes", [])) for m in modules_data),
                "average_complexity": project_metrics.get("avg_complexity", 0),
                "complexity_distribution": complexity_dist,
                "most_complex_modules": sorted(
                    [(m["path"], m["complexity"]) for m in modules_data],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            },
            "dependencies": deps_data,
            "debt": tech_debt,
            "optimizations": optimization_suggestions,
            "security": security_list,
            "entry_points": entry_points,
            "patterns": {}, # TODO: Extraer detección de patrones
        }

        # 8. Generar reportes
        try:
            reporting.generate_project_summary(
                results, 
                self.project_path / "PROJECT_SUMMARY.md",
                self.project_path.name
            )
            reporting.generate_ai_context(
                results, 
                self.project_path / "AI_CONTEXT.md",
                self.project_path.name
            )
            
            # Guardar JSON completo
            with open(self.project_path / "project_context.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"Error generando reportes: {e}")

        logger.info(f"Análisis completado en {time.time() - start_time:.2f}s")
        return results

    def _analyze_modules_parallel(self, files: List[pathlib.Path]) -> List[Dict[str, Any]]:
        """Analiza módulos en paralelo."""
        results = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._analyze_single_module, f): f 
                for f in files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                f = future_to_file[future]
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                except Exception as e:
                    logger.error(f"Error analizando {f}: {e}")
                    self.error_log[str(f)] = str(e)
                    
        return results

    def _analyze_single_module(self, file_path: pathlib.Path) -> Dict[str, Any]:
        """Analiza un solo módulo (método estático compatible para pickling si fuera necesario)."""
        # Nota: ProcessPoolExecutor requiere que esto sea pickleable. 
        # Si usamos métodos de instancia, self debe ser pickleable.
        # ProjectAnalyzer es pickleable si sus atributos lo son.
        
        try:
            content = fs_utils.read_file_fast(file_path)
            if not content:
                return {}

            tree = ast.parse(content)
            
            # Métricas AST
            return {
                "path": str(file_path.relative_to(self.project_path)),
                "lines": len(content.splitlines()),
                "file_size_kb": file_path.stat().st_size / 1024,
                "complexity": ast_utils.calculate_complexity(tree),
                "imports": ast_utils.extract_imports(tree),
                "classes": ast_utils.extract_classes(tree),
                "functions": ast_utils.extract_functions(tree),
                "docstrings": ast_utils.check_docstrings(tree),
                "has_main": ast_utils.has_main_guard(tree),
                "type_hints": ast_utils.calculate_type_hint_coverage(tree),
                "halstead": ast_utils.calculate_halstead_metrics(tree),
                "syntax_error": False
            }

        except SyntaxError:
            return {
                "path": str(file_path.relative_to(self.project_path)),
                "syntax_error": True,
                "error": "SyntaxError"
            }
        except Exception as e:
            return {
                "path": str(file_path.relative_to(self.project_path)),
                "syntax_error": True, # Tratamos como error
                "error": str(e)
            }
