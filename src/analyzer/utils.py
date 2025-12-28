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

import threading
import time
import sys
import pathlib
from collections import OrderedDict
from typing import Any, List, Dict
from contextlib import contextmanager
import signal

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
        self.file_times = []
        self.last_update = 0

    def update(self, file_path: pathlib.Path, processing_time: float) -> None:
        self.processed += 1
        self.file_times.append(processing_time)
        current_time = time.time()
        if self.processed % 10 == 0 or current_time - self.last_update > 2:
            self._display_progress()
            self.last_update = current_time

    def _display_progress(self) -> None:
        elapsed = time.time() - self.start_time
        percent = (self.processed / self.total) * 100 if self.total > 0 else 0
        if self.file_times and self.processed > 0:
            avg_time = sum(self.file_times) / len(self.file_times)
            remaining = self.total - self.processed
            eta = remaining * avg_time
            eta_str = f"{eta:.0f}s"
        else:
            eta_str = "..."
        sys.stdout.write(f"\r\033[K📊 Progress: {self.processed}/{self.total} ({percent:.1f}%) | ETA: {eta_str}")
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
