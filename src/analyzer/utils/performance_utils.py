"""Performance and progress tracking utilities."""

import pathlib
import signal
import sys
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from typing import Any, Dict


class LRUCache:
    """Efficient Least Recently Used (LRU) Cache.

    Attributes:
        maxsize: Maximum number of items in the cache.
    """

    def __init__(self, maxsize: int = 256):
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self._lock = threading.Lock()
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any:
        """Retrieves an item from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value or None if not found.
        """
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """Adds an item to the cache.

        Args:
            key: The cache key.
            value: The value to store.
        """
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def stats(self) -> Dict[str, Any]:
        """Returns cache performance statistics.

        Returns:
            A dictionary with size, hits, misses, and hit rate.
        """
        with self._lock:
            total = self.hits + self.misses
            return {
                "size": len(self.cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": self.hits / total if total > 0 else 0,
            }


class ProgressTracker:
    """Real-time progress tracker for file processing.

    Attributes:
        total: Total number of files to process.
    """

    def __init__(self, total_files: int):
        self.total = total_files
        self.processed = 0
        self.start_time = time.time()
        self.avg_time = 0.0
        self.last_update = 0.0

    def update(self, file_path: pathlib.Path, processing_time: float) -> None:
        """Updates the progress status.

        Args:
            file_path: Current file path.
            processing_time: Time taken to process the file.
        """
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
        """Finalizes the progress tracking and returns final metrics.

        Returns:
            A dictionary with elapsed time and throughput.
        """
        elapsed = time.time() - self.start_time
        print()
        return {
            "elapsed": elapsed,
            "files_per_second": self.processed / elapsed if elapsed > 0 else 0,
        }


@contextmanager
def timeout_manager(seconds: int):
    """Context manager for enforcing operation timeouts.

    Args:
        seconds: Timeout duration in seconds.
    """

    def signal_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds}s")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
