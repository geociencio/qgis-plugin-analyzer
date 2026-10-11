"""Incremental per-file analysis cache keyed by content hash.

The cache lets repeated runs reuse a module's :class:`ModuleAnalysisResult`
when neither the file content nor the effective analysis configuration has
changed. Invalidation is driven by a signature that folds in the analyzer
version, a fingerprint of the analyzer package source, the resolved project
path, and the effective rules/scope/content configuration — so a change in the
analysis logic, the configuration, or the project itself discards the cache.
"""

import hashlib
import json
import logging
import pathlib
from typing import Any

from .scanner import ModuleAnalysisResult

CACHE_SCHEMA = 1
CACHE_FILENAME = ".analyzer_cache.json"

logger = logging.getLogger("qgis_analyzer")


def file_content_hash(path: pathlib.Path) -> str:
    """Return the SHA-256 hexdigest of a file's raw bytes.

    Args:
        path: File to hash.

    Returns:
        The hexadecimal SHA-256 digest of the file contents.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyzer_fingerprint() -> str:
    """Return a fingerprint of the analyzer package source.

    The walk is anchored to this file's package directory (not a CWD-relative
    path), so it is correct both in the ``src/`` layout and when installed as a
    wheel. Any change to the analyzer's own code invalidates the cache.

    Returns:
        The hexadecimal SHA-256 digest over ``(relative_path, content_hash)`` of
        every ``*.py`` file in the analyzer package, in sorted order.
    """
    package_root = pathlib.Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for py_file in sorted(package_root.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        rel = py_file.relative_to(package_root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(file_content_hash(py_file).encode("utf-8"))
    return digest.hexdigest()


def cache_signature(
    analyzer_version: str,
    *,
    project_path: pathlib.Path,
    rules_config: dict[str, Any],
    scope: str,
    include_content: bool,
    project_type: str,
) -> str:
    """Return the signature that invalidates the cache when inputs change.

    Args:
        analyzer_version: Installed analyzer version.
        project_path: Root path of the analyzed project (resolved).
        rules_config: Effective rule configuration.
        scope: Analysis scope.
        include_content: Whether source content is embedded in results.
        project_type: Detected project type ('qgis' or 'generic').

    Returns:
        A hexadecimal SHA-256 digest of the invalidation inputs.
    """
    payload = {
        "schema": CACHE_SCHEMA,
        "analyzer_version": analyzer_version,
        "fingerprint": analyzer_fingerprint(),
        "project_path": str(pathlib.Path(project_path).resolve()),
        "rules_config": rules_config,
        "scope": scope,
        "include_content": include_content,
        "project_type": project_type,
    }
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class ModuleCache:
    """A content-addressed cache of per-module analysis results.

    Attributes:
        path: Location of the cache file.
        signature: Effective signature; a mismatch discards the loaded cache.
    """

    def __init__(self, path: pathlib.Path, signature: str, analyzer_version: str) -> None:
        """Initialize the cache.

        Args:
            path: Location of the cache file.
            signature: Signature computed by :func:`cache_signature`.
            analyzer_version: Installed analyzer version (stored for diagnostics).
        """
        self.path = path
        self.signature = signature
        self.analyzer_version = analyzer_version
        self._entries: dict[str, dict[str, Any]] = {}
        self._current: dict[str, dict[str, Any]] = {}

    def load(self) -> None:
        """Load entries from disk, ignoring missing/corrupt/mismatched caches."""
        self._entries = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        if not isinstance(data, dict):
            return
        if data.get("schema") != CACHE_SCHEMA or data.get("signature") != self.signature:
            logger.debug("Module cache signature mismatch; ignoring existing cache.")
            return

        entries = data.get("entries")
        if isinstance(entries, dict):
            self._entries = {
                key: value for key, value in entries.items() if isinstance(value, dict)
            }

    def lookup(self, rel_path: str, content_hash: str) -> ModuleAnalysisResult | None:
        """Return the cached result for a file if it matches ``content_hash``.

        Records reuse for the current run so :meth:`save` can retain it.

        Args:
            rel_path: Project-relative module path.
            content_hash: Content hash of the file this run.

        Returns:
            The cached result, or None on a miss.
        """
        entry = self._entries.get(rel_path)
        if isinstance(entry, dict) and entry.get("hash") == content_hash:
            result = entry.get("result")
            if isinstance(result, dict):
                self._current[rel_path] = {"hash": content_hash, "result": result}
                return result  # type: ignore[return-value]
        return None

    def store(self, rel_path: str, content_hash: str, result: ModuleAnalysisResult) -> None:
        """Record a freshly computed result for the current run.

        Args:
            rel_path: Project-relative module path.
            content_hash: Content hash of the file this run.
            result: The computed module analysis result.
        """
        self._current[rel_path] = {"hash": content_hash, "result": result}

    def save(self) -> None:
        """Persist the current run's entries, pruning files no longer present."""
        if not self._current:
            return
        payload = {
            "schema": CACHE_SCHEMA,
            "analyzer_version": self.analyzer_version,
            "signature": self.signature,
            "entries": self._current,
        }
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(payload), encoding="utf-8")
        except OSError as exc:
            logger.warning(f"⚠️  Could not write module cache: {exc}")


def build_cache(
    *,
    enabled: bool,
    project_path: pathlib.Path,
    output_dir: pathlib.Path,
    analyzer_version: str,
    rules_config: dict[str, Any],
    scope: str,
    include_content: bool,
    project_type: str,
) -> ModuleCache | None:
    """Build and load the per-file cache, or return None when disabled.

    Args:
        enabled: Whether caching is enabled (profile/CLI).
        project_path: Root path of the analyzed project.
        output_dir: Directory where the cache file lives.
        analyzer_version: Installed analyzer version.
        rules_config: Effective rule configuration.
        scope: Analysis scope.
        include_content: Whether source content is embedded in results.
        project_type: Detected project type ('qgis' or 'generic').

    Returns:
        A loaded :class:`ModuleCache`, or None when ``enabled`` is False.
    """
    if not enabled:
        return None
    signature = cache_signature(
        analyzer_version,
        project_path=project_path,
        rules_config=rules_config,
        scope=scope,
        include_content=include_content,
        project_type=project_type,
    )
    cache = ModuleCache(output_dir / CACHE_FILENAME, signature, analyzer_version)
    cache.load()
    return cache
