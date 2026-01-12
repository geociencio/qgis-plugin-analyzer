
import os
import pathlib
import fnmatch
import mmap
import subprocess
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LRUCache:
    """Cache simple para archivos."""
    def __init__(self, maxsize: int = 256):
        self.cache = {}
        self.maxsize = maxsize

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value: Any):
        if len(self.cache) > self.maxsize:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
        
    def clear(self):
        self.cache.clear()

# Global cache instance
file_cache = LRUCache()

def read_file_fast(path: pathlib.Path) -> str:
    """Lectura ultra rápida con memory mapping y cache."""
    cache_key = str(path)
    cached = file_cache.get(cache_key)
    if cached:
        return cached

    try:
        with open(path, "rb") as f:
            file_size = path.stat().st_size

            # Usar memory mapping para archivos grandes (> 1MB)
            if file_size > 1024 * 1024:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    content = mm.read().decode("utf-8-sig", errors="replace")
            else:
                # Para archivos pequeños, lectura directa
                content = f.read().decode("utf-8-sig", errors="replace")

            # Cachear resultado
            file_cache.set(cache_key, content)
            return content

    except Exception as e:
        logger.warning(f"⚠️ Error lectura {path}: {e}")
        return ""

def load_exclusion_patterns(project_path: pathlib.Path, extra_patterns: List[str] = None) -> List[str]:
    """Carga patrones de exclusión."""
    patterns = []
    
    # 1. Prioridad: .analyzerignore
    ignore_file = project_path / ".analyzerignore"
    if ignore_file.exists():
        try:
            with open(ignore_file, encoding="utf-8") as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except:
            pass

    # 2. Defaults
    if not patterns:
        patterns = [
            "__pycache__", ".git", ".venv", "venv", "env", ".tox", ".pytest_cache",
            ".mypy_cache", ".coverage", "build", "dist", "*.egg-info"
        ]

    if extra_patterns:
        patterns.extend(extra_patterns)

    return patterns

def is_test_file(path: pathlib.Path) -> bool:
    """Determina si es archivo de tests."""
    filename = path.name.lower()
    test_patterns = ["test_", "_test", "spec_", "_spec", "conftest"]

    return (
        any(pattern in filename for pattern in test_patterns)
        or "tests" in str(path).lower()
        or "test" in path.parent.name.lower()
    )

def count_test_files(project_path: pathlib.Path) -> int:
    """Cuenta archivos de test."""
    count = 0
    for file in project_path.rglob("*.py"):
        if is_test_file(file):
            count += 1
    return count

def get_python_files_filtered(project_path: pathlib.Path, exclusion_patterns: List[str]) -> List[pathlib.Path]:
    """Obtener archivos Python con filtrado."""
    python_files = []

    for py_file in project_path.rglob("*.py"):
        rel_path = str(py_file.relative_to(project_path))
        
        should_exclude = False
        for pattern in exclusion_patterns:
            if pattern.endswith("/"):
                pattern = pattern[:-1]

            if (
                fnmatch.fnmatch(rel_path, pattern)
                or fnmatch.fnmatch(py_file.name, pattern)
                or any(fnmatch.fnmatch(part, pattern) for part in py_file.relative_to(project_path).parts)
            ):
                should_exclude = True
                break
        
        if should_exclude:
            continue

        if is_test_file(py_file):
            continue

        python_files.append(py_file)

    return sorted(python_files)

def generate_tree_optimized(project_path: pathlib.Path) -> str:
    """Genera árbol de directorios optimizado."""
    try:
        result = subprocess.run(
            ["tree", "-I", "__pycache__|*.pyc|*.pyo|*.pycache|.git|.venv|venv|env", "-a", "--noreport", "-L", "4"],
            check=False, cwd=project_path, capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            return result.stdout[:1500]
    except:
        pass

    tree_lines = ["./"]
    max_depth = 4
    max_files_per_dir = 8

    for root, dirs, files in os.walk(project_path):
        depth = root[len(str(project_path)):].count(os.sep)
        if depth > max_depth:
            continue

        dirs[:] = [d for d in dirs if not d.startswith((".", "_"))]

        indent = "    " * depth
        rel_path = os.path.relpath(root, project_path)
        if rel_path != ".":
            tree_lines.append(f"{indent}{os.path.basename(root)}/")

        file_indent = "    " * (depth + 1)
        for i, file in enumerate(sorted(files)[:max_files_per_dir]):
            if i == max_files_per_dir - 1 and len(files) > max_files_per_dir:
                tree_lines.append(f"{file_indent}... (+{len(files) - max_files_per_dir} más)")
                break
            tree_lines.append(f"{file_indent}{file}")

    return "\n".join(tree_lines)

def count_file_types(project_path: pathlib.Path) -> Dict[str, int]:
    extensions = {}
    common_exts = {".py", ".txt", ".md", ".json", ".yml", ".yaml", ".html", ".css", ".js", ".xml", ".csv", ".sql"}

    for file in project_path.rglob("*"):
        if file.is_file():
            ext = file.suffix.lower()
            if ext in common_exts or ext:
                extensions[ext] = extensions.get(ext, 0) + 1

    return dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:20])

def calculate_size_stats(project_path: pathlib.Path) -> Dict[str, Any]:
    total_files = 0
    total_size = 0
    python_files = 0
    python_size = 0

    for entry in os.scandir(project_path):
        if entry.is_file():
            total_files += 1
            total_size += entry.stat().st_size
            if entry.name.endswith(".py"):
                python_files += 1
                python_size += entry.stat().st_size
        elif entry.is_dir() and not entry.name.startswith("."):
            for root, _dirs, files in os.walk(entry.path):
                for file in files:
                    total_files += 1
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        if file.endswith(".py"):
                            python_files += 1
                            python_size += file_size
                    except:
                        pass

    return {
        "total_files": total_files,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "python_files": python_files,
        "python_size_mb": round(python_size / (1024 * 1024), 2),
        "avg_file_size_kb": round(total_size / total_files / 1024, 2) if total_files > 0 else 0,
        "python_percentage": round(python_size / total_size * 100, 2) if total_size > 0 else 0,
    }

def analyze_structure(project_path: pathlib.Path, modules_count: int) -> Dict[str, Any]:
    return {
        "tree": generate_tree_optimized(project_path),
        "modules_count": modules_count,
        "file_types": count_file_types(project_path),
        "size_stats": calculate_size_stats(project_path),
    }
