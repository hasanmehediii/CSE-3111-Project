"""Lightweight process-wide counters for cache performance.

Tracks hits, misses, bytes served from cache vs origin, blocked requests,
and the count of currently cached entries (peak).
"""
import threading


class CacheStats:
    def __init__(self):
        self._lock = threading.Lock()
        self.cache_hits = 0
        self.cache_misses = 0
        self.bytes_from_cache = 0
        self.bytes_from_origin = 0
        self.blocked_blacklist = 0
        self.blocked_content = 0
        self.errors = 0
        self.peak_cached = 0

    def record_hit(self, bytes_served):
        with self._lock:
            self.cache_hits += 1
            self.bytes_from_cache += bytes_served

    def record_miss(self, bytes_served):
        with self._lock:
            self.cache_misses += 1
            self.bytes_from_origin += bytes_served

    def record_blacklist(self):
        with self._lock:
            self.blocked_blacklist += 1

    def record_content_block(self):
        with self._lock:
            self.blocked_content += 1

    def record_error(self):
        with self._lock:
            self.errors += 1

    def update_peak(self, current_size):
        with self._lock:
            if current_size > self.peak_cached:
                self.peak_cached = current_size

    def snapshot(self):
        with self._lock:
            total = self.cache_hits + self.cache_misses
            hit_ratio = (self.cache_hits / total) if total else 0.0
            return {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "hit_ratio": round(hit_ratio, 4),
                "bytes_from_cache": self.bytes_from_cache,
                "bytes_from_origin": self.bytes_from_origin,
                "bytes_saved": self.bytes_from_cache,
                "blocked_blacklist": self.blocked_blacklist,
                "blocked_content": self.blocked_content,
                "errors": self.errors,
                "peak_cached": self.peak_cached,
            }

    def reset(self):
        with self._lock:
            self.__init__()


stats = CacheStats()
