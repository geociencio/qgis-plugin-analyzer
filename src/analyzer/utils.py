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
import fnmatch
import logging
import os
import pathlib
import re
import signal
import sys
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from typing import Any, Dict, List

def setup_logger(output_dir: pathlib.Path) -> logging.Logger:
    """Configures the global logger with console and file handlers."""
    logger = logging.getLogger("qgis_analyzer")
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Formatters
    console_fmt = logging.Formatter("%(message)s")
    file_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console Handler (User facing)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(console_fmt)
    logger.addHandler(ch)

    # File Handler (Detailed debugging)
    log_file = output_dir / "analyzer.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(file_fmt)
    logger.addHandler(fh)

    return logger

# Global logger instance (will be configured in cli.py or engine.py)
logger = logging.getLogger("qgis_analyzer")


def _minimal_toml_load(file_obj) -> Dict[str, Any]:
    """
    EXTREMELY minimal TOML parser focused ONLY on extracting 
    [tool.qgis-analyzer.profiles] from pyproject.toml.
    Does not handle nested structures or full TOML spec.
    """
    data = {"tool": {"qgis-analyzer": {"profiles": {}}}}
    current_section = None
    
    # Simple regex to catch [tool.qgis-analyzer.profiles.NAME]
    profile_regex = re.compile(r'^\[tool\.qgis-analyzer\.profiles\.([\w-]+)\]')
    
    try:
        content = file_obj.read().decode("utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Check for section header
            if line.startswith("[") and line.endswith("]"):
                match = profile_regex.match(line)
                if match:
                    current_section = match.group(1)
                    data["tool"]["qgis-analyzer"]["profiles"][current_section] = {}
                else:
                    current_section = None
                continue
            
            # Key-value pair
            if current_section and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                
                # Basic type conversion
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                elif val.isdigit():
                    val = int(val)
                elif val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.startswith("'") and val.endswith("'"):
                    val = val[1:-1]
                
                data["tool"]["qgis-analyzer"]["profiles"][current_section][key] = val
    except Exception as e:
        logger.error(f"Error in minimal TOML parser: {e}")
        
    return data


try:
    import tomllib
except ImportError:
    # Use our minimal fallback if tomllib is not available (Python < 3.11)
    tomllib = None


class LRUCache:
    """Efficient LRU Cache."""

    def __init__(self, maxsize: int = 256):
        self.cache = OrderedDict()
        self._lock = threading.Lock()
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any:
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self.hits + self.misses
            return {
                "size": len(self.cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": self.hits / total if total > 0 else 0,
            }


class ProgressTracker:
    """Real-time progress tracker."""

    def __init__(self, total_files: int):
        self.total = total_files
        self.processed = 0
        self.start_time = time.time()
        self.avg_time = 0.0
        self.last_update = 0

    def update(self, file_path: pathlib.Path, processing_time: float) -> None:
        self.processed += 1
        # Simple moving average for ETA
        if self.avg_time == 0:
            self.avg_time = processing_time
        else:
            self.avg_time = (self.avg_time * 0.9) + (processing_time * 0.1)
            
        current_time = time.time()
        if self.processed % 10 == 0 or current_time - self.last_update > 2:
            self._display_progress()
            self.last_update = current_time

    def _display_progress(self) -> None:
        percent = (self.processed / self.total) * 100 if self.total > 0 else 0
        if self.processed > 0:
            remaining = self.total - self.processed
            eta = remaining * self.avg_time
            eta_str = f"{eta:.0f}s"
        else:
            eta_str = "..."
        sys.stdout.write(
            f"\r\033[K📊 Progress: {self.processed}/{self.total} ({percent:.1f}%) | ETA: {eta_str}"
        )
        sys.stdout.flush()

    def complete(self) -> Dict[str, Any]:
        elapsed = time.time() - self.start_time
        print()
        return {
            "elapsed": elapsed,
            "files_per_second": self.processed / elapsed if elapsed > 0 else 0,
        }


@contextmanager
def timeout_manager(seconds: int):
    """Context manager for timeouts."""

    def signal_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds}s")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class IgnoreMatcher:
    """Handles .analyzerignore patterns using fnmatch."""

    def __init__(self, root_path: pathlib.Path, patterns: List[str]):
        self.root_path = root_path
        self.patterns = [p.strip() for p in patterns if p.strip() and not p.startswith("#")]
        self._cache = {}

    def is_ignored(self, path: pathlib.Path) -> bool:
        """Returns True if the path matches any of the ignore patterns."""
        str_path = str(path)
        if str_path in self._cache:
            return self._cache[str_path]
            
        try:
            rel_path = path.relative_to(self.root_path)
            str_rel_path = str(rel_path)
            result = self._check_patterns(str_rel_path, path.name)
            self._cache[str_path] = result
            return result
        except ValueError:
            return False

    def _check_patterns(self, str_rel_path: str, name: str) -> bool:
        for pattern in self.patterns:
            # Handle directory-specific patterns (ending in /)
            if pattern.endswith("/"):
                # If the pattern is 'dir/', match any path that starts with 'dir/'
                clean_pattern = pattern.rstrip("/")
                if str_rel_path.startswith(clean_pattern + os.sep) or str_rel_path == clean_pattern:
                    return True
            # Standard glob matching
            if fnmatch.fnmatch(str_rel_path, pattern):
                return True
            # Match basename if pattern doesn't contain a slash
            if "/" not in pattern and fnmatch.fnmatch(name, pattern):
                return True
        return False


def load_ignore_patterns(ignore_file: pathlib.Path) -> List[str]:
    """Loads ignore patterns from a file."""
    if not ignore_file.exists():
        return []
    with open(ignore_file) as f:
        return f.readlines()


def load_profile_config(
    project_path: pathlib.Path, profile_name: str = "default"
) -> Dict[str, Any]:
    """Loads a specific profile configuration from pyproject.toml."""
    pyproject = project_path / "pyproject.toml"
    default_config = {"strict": False, "generate_html": True, "fail_on_error": False}

    if not pyproject.exists():
        return default_config

    try:
        with open(pyproject, "rb") as f:
            if tomllib:
                data = tomllib.load(f)
            else:
                data = _minimal_toml_load(f)

        profiles = data.get("tool", {}).get("qgis-analyzer", {}).get("profiles", {})
        profile_data = profiles.get(profile_name)

        if not profile_data:
            if profile_name != "default":
                logger.warning(f"Profile '{profile_name}' not found. Using default values.")
            return default_config

        return {**default_config, **profile_data}
    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        return default_config
