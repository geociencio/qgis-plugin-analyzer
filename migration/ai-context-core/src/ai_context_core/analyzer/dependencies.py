
from typing import Dict, Any, List, Set, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def count_edges(import_graph: Dict[str, Set[str]]) -> int:
    """Cuenta total de aristas en el grafo."""
    return sum(len(neighbors) for neighbors in import_graph.values())

def find_simple_cycles(import_graph: Dict[str, Set[str]], limit: int = 5) -> List[List[str]]:
    """Detecta ciclos simples usando DFS."""
    cycles = []
    visited = set()
    path = []
    path_set = set()

    def dfs(u):
        if len(cycles) >= limit:
            return

        visited.add(u)
        path.append(u)
        path_set.add(u)

        if u in import_graph:
            for v in import_graph[u]:
                if v in path_set:
                    # Ciclo detectado
                    cycle_start = path.index(v)
                    cycles.append(path[cycle_start:])
                elif v not in visited:
                    dfs(v)

        path_set.remove(u)
        path.pop()

    for node in list(import_graph.keys()):
        if node not in visited:
            dfs(node)

    return cycles

def count_connected_components(import_graph: Dict[str, Set[str]]) -> int:
    """Cuenta componentes débilmente conectados."""
    # Convertir a no dirigido
    undirected = {}
    for u, neighbors in import_graph.items():
        if u not in undirected:
            undirected[u] = set()
        for v in neighbors:
            undirected[u].add(v)
            if v not in undirected:
                undirected[v] = set()
            undirected[v].add(u)

    visited = set()
    count = 0

    for node in undirected:
        if node not in visited:
            count += 1
            # BFS
            queue = [node]
            visited.add(node)
            while queue:
                curr = queue.pop(0)
                for neighbor in undirected.get(curr, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
    return count

def analyze_dependencies(modules_data: List[Dict[str, Any]], project_path: Path, read_file_func) -> Dict[str, Any]:
    """Analiza dependencias del proyecto de forma optimizada."""
    dependencies = {
        "internal": [],
        "external": [],
        "third_party": [],
        "files": {},
        "import_graph": {},
        "circular_dependencies": [],
        "graph_metrics": {},
    }

    # Analizar archivos de dependencias comunes
    req_files = [
        "requirements.txt",
        "setup.py",
        "pyproject.toml",
        "Pipfile",
        "setup.cfg",
        "environment.yml",
    ]

    for req_file in req_files:
        path = project_path / req_file
        if path.exists():
            try:
                content = read_file_func(path)
                if content:
                    dependencies["files"][req_file] = content[:2000]  # Limitar tamaño
            except:
                pass

    # Construir grafo de dependencias
    import_graph = {}
    all_imports = set()

    for module in modules_data:
        module_path = module.get("path", "")
        imports = module.get("imports", [])

        if module_path:
            # Añadir nodo
            if module_path not in import_graph:
                import_graph[module_path] = set()

            all_imports.update(imports)

            # Añadir aristas al grafo
            for imp in imports:
                # Buscar si la importación corresponde a un módulo del proyecto
                for other_module in modules_data:
                    other_path = other_module.get("path", "")
                    if other_path and other_path.replace(".py", "").replace("/", ".") in imp:
                        # Añadir edge: module_path -> other_path
                        import_graph[module_path].add(other_path)
                        # Asegurar que el destino también existe como nodo
                        if other_path not in import_graph:
                            import_graph[other_path] = set()

    dependencies["import_graph"] = {k: list(v) for k, v in import_graph.items()} # Serializable

    # Detectar dependencias circulares
    try:
        cycles = find_simple_cycles(import_graph, limit=5)
        if cycles:
            dependencies["circular_dependencies"] = cycles
    except:
        pass

    # Calcular métricas del grafo
    num_nodes = len(import_graph)
    if num_nodes > 0:
        try:
            num_edges = count_edges(import_graph)
            # Density for directed graph: E / (V * (V - 1))
            max_edges = num_nodes * (num_nodes - 1)
            density = num_edges / max_edges if max_edges > 0 else 0

            dependencies["graph_metrics"] = {
                "nodes": num_nodes,
                "edges": num_edges,
                "density": density,
                "is_dag": len(find_simple_cycles(import_graph, limit=1)) == 0,
                "weakly_connected_components": count_connected_components(import_graph),
            }
        except Exception as e:
            logger.exception(f"Error calculando métricas de grafo: {e}")

    # Clasificar imports
    stdlib_modules = {
        "os", "sys", "json", "pathlib", "typing", "datetime", "re", "collections",
        "itertools", "math", "random", "statistics", "functools", "hashlib",
        "base64", "csv", "pickle", "sqlite3", "subprocess", "logging", "time", "traceback"
    }

    for imp in sorted(all_imports):
        # Determinar si es import interno (relativo)
        if imp.startswith(".") or any(seg in imp for seg in ["..", "./"]):
            dependencies["internal"].append(imp)
        # Determinar si es stdlib
        elif imp.split(".")[0] in stdlib_modules:
            dependencies["external"].append(imp)
        else:
            dependencies["third_party"].append(imp)

    return dependencies
