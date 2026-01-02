"""Utilities package for the QGIS Plugin Analyzer."""

from .ast_utils import (
    calculate_complexity,
    calculate_module_complexity,
    check_main_guard,
    extract_classes_from_ast,
    extract_functions_from_ast,
    extract_imports_from_ast,
)
from .config_utils import _minimal_toml_load, load_profile_config
from .logging_utils import logger, setup_logger
from .path_utils import (
    DEFAULT_EXCLUDE,
    IgnoreMatcher,
    load_ignore_patterns,
    safe_path_resolve,
)
from .performance_utils import LRUCache, ProgressTracker, timeout_manager

__all__ = [
    "calculate_complexity",
    "extract_functions_from_ast",
    "extract_classes_from_ast",
    "extract_imports_from_ast",
    "calculate_module_complexity",
    "check_main_guard",
    "setup_logger",
    "logger",
    "safe_path_resolve",
    "IgnoreMatcher",
    "load_ignore_patterns",
    "DEFAULT_EXCLUDE",
    "load_profile_config",
    "_minimal_toml_load",
    "LRUCache",
    "ProgressTracker",
    "timeout_manager",
]
