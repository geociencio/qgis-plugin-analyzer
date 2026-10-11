"""Parallel AST analysis runner.

Extracted from :mod:`analyzer.engine` to keep the orchestrator within the
project's module-size limit. Owns the process-pool setup, file batching,
progress tracking and the incremental per-file cache.
"""

import pathlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any

from .module_cache import ModuleCache, file_content_hash
from .scanner import (
    ModuleAnalysisResult,
    _get_relative_path,
    analyze_chunk_worker,
    init_worker,
)
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


def _safe_content_hash(path: pathlib.Path) -> str | None:
    """Return the content hash of a file, or None when it cannot be read."""
    try:
        return file_content_hash(path)
    except OSError:
        return None


def _partition_cached(
    files: list[pathlib.Path],
    project_path: pathlib.Path,
    cache: ModuleCache,
) -> tuple[dict[str, ModuleAnalysisResult], list[tuple[pathlib.Path, str, str | None]]]:
    """Split the file list into cache hits and misses.

    Args:
        files: Files to analyze.
        project_path: Root path of the project.
        cache: Per-file cache to consult.

    Returns:
        A tuple ``(hits, misses)`` where ``hits`` maps module path to a reused
        result and ``misses`` holds ``(file, rel_path, content_hash)`` tuples.
    """
    hits: dict[str, ModuleAnalysisResult] = {}
    misses: list[tuple[pathlib.Path, str, str | None]] = []

    for py_file in files:
        try:
            rel_path = _get_relative_path(py_file, project_path)
        except ValueError:
            continue

        content_hash = _safe_content_hash(py_file)
        cached = cache.lookup(rel_path, content_hash) if content_hash else None
        if cached is not None:
            hits[rel_path] = cached
        else:
            misses.append((py_file, rel_path, content_hash))

    return hits, misses


def _run_pool(
    files: list[pathlib.Path],
    rules_config: dict[str, Any],
    scope: str,
    *,
    project_path: pathlib.Path,
    max_workers: int,
    include_content: bool,
) -> list[ModuleAnalysisResult]:
    """Analyze a batch of files through the process pool.

    Args:
        files: Files to analyze (the cache misses).
        rules_config: Rule-specific configuration overrides.
        scope: The analysis scope.
        project_path: Root path of the project being analyzed.
        max_workers: Number of worker processes.
        include_content: Whether to embed source content in the results.

    Returns:
        The list of module analysis results produced by the workers.
    """
    tracker = ProgressTracker(len(files))
    results: list[ModuleAnalysisResult] = []

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
            results.extend(future.result())
            for py_file in futures[future]:
                tracker.update(py_file, 0)

    tracker.complete()
    return results


def _store_misses(
    cache: ModuleCache,
    misses: list[tuple[pathlib.Path, str, str | None]],
    results_by_path: dict[str, ModuleAnalysisResult],
) -> None:
    """Cache the freshly computed results for each miss."""
    for _, rel_path, content_hash in misses:
        result = results_by_path.get(rel_path)
        if result is not None and content_hash is not None:
            cache.store(rel_path, content_hash, result)


def run_parallel_analysis(
    files: list[pathlib.Path],
    rules_config: dict[str, Any],
    scope: str,
    *,
    project_path: pathlib.Path,
    max_workers: int,
    include_content: bool,
    cache: ModuleCache | None = None,
) -> list[ModuleAnalysisResult]:
    """Runs parallel analysis on all Python files, reusing cached results.

    Files whose content and configuration are unchanged (a cache hit) are
    resolved in the parent process; only cache misses are sent to the worker
    pool. The returned list is sorted by module path, making the output
    deterministic (and therefore identical whether or not the cache is warm).

    Args:
        files: List of paths to analyze.
        rules_config: Rule-specific configuration overrides.
        scope: The analysis scope.
        project_path: Root path of the project being analyzed.
        max_workers: Number of worker processes.
        include_content: Whether to embed source content in the results.
        cache: Optional per-file cache; when None no reuse or persistence occurs.

    Returns:
        A list of module analysis results, sorted by module path.
    """
    if cache is None:
        results = _run_pool(
            files,
            rules_config,
            scope,
            project_path=project_path,
            max_workers=max_workers,
            include_content=include_content,
        )
        return sorted(results, key=lambda result: result["path"])

    results_by_path, misses = _partition_cached(files, project_path, cache)

    if misses:
        missing_files = [py_file for py_file, _, _ in misses]
        for result in _run_pool(
            missing_files,
            rules_config,
            scope,
            project_path=project_path,
            max_workers=max_workers,
            include_content=include_content,
        ):
            results_by_path[result["path"]] = result
        _store_misses(cache, misses, results_by_path)

    cache.save()

    return [results_by_path[path] for path in sorted(results_by_path)]
