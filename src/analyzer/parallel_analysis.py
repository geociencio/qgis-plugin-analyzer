"""Parallel AST analysis runner.

Extracted from :mod:`analyzer.engine` to keep the orchestrator within the
project's module-size limit. Owns the process-pool setup, file batching and
progress tracking.
"""

import pathlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any

from .scanner import ModuleAnalysisResult, analyze_chunk_worker, init_worker
from .utils import ProgressTracker


def chunk_files(files: list[pathlib.Path], max_workers: int) -> list[list[pathlib.Path]]:
    """Splits the file list into batches sized for the worker pool.

    Args:
        files: Files to analyze.
        max_workers: Number of worker processes (used to size the batches).

    Returns:
        A list of file batches (at least one, even for an empty input).
    """
    if not files:
        return []
    chunk_size = max(1, len(files) // (max_workers * 4))
    return [files[i : i + chunk_size] for i in range(0, len(files), chunk_size)]


def run_parallel_analysis(
    files: list[pathlib.Path],
    rules_config: dict[str, Any],
    scope: str,
    *,
    project_path: pathlib.Path,
    max_workers: int,
    include_content: bool,
) -> list[ModuleAnalysisResult]:
    """Runs parallel analysis on all Python files.

    Args:
        files: List of paths to analyze.
        rules_config: Rule-specific configuration overrides.
        scope: The analysis scope.
        project_path: Root path of the project being analyzed.
        max_workers: Number of worker processes.
        include_content: Whether to embed source content in the results.

    Returns:
        A list of module analysis results.
    """
    tracker = ProgressTracker(len(files))
    modules_data: list[ModuleAnalysisResult] = []

    # Shared context to avoid serializing large rules multiple times
    shared_context = {
        "project_path": project_path,
        "rules_config": rules_config,
        "scope": scope,
        "include_content": include_content,
    }

    # Batch files to amortize per-task IPC overhead on large projects.
    chunks = chunk_files(files, max_workers)

    with ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=init_worker,
        initargs=(shared_context,),
    ) as executor:
        # We no longer need to pass project_path or rules_config to every call
        futures = {executor.submit(analyze_chunk_worker, chunk): chunk for chunk in chunks}
        for future in as_completed(futures):
            modules_data.extend(future.result())
            for py_file in futures[future]:
                tracker.update(py_file, 0)

    tracker.complete()
    return modules_data
