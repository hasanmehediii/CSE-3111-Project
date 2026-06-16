"""Thread-safe in-memory cache with TTL."""
import time
import threading


class MemoryCache:
    def __init__(self, ttl=300):
        self.storage = {}
        self.ttl = ttl
        self.lock = threading.Lock()

    def _prune_locked(self):
        now = time.time()
        expired = [k for k, v in self.storage.items() if now - v["timestamp"] > self.ttl]
        for k in expired:
            del self.storage[k]

    def set(self, url, content):
        with self.lock:
            self.storage[url] = {"content": content, "timestamp": time.time()}

    def get(self, url):
        with self.lock:
            data = self.storage.get(url)
            if not data:
                return None
            if time.time() - data["timestamp"] > self.ttl:
                del self.storage[url]
                return None
            return data["content"]

    def keys(self):
        with self.lock:
            self._prune_locked()
            return list(self.storage.keys())

    def size(self):
        with self.lock:
            self._prune_locked()
            return len(self.storage)

    def delete(self, url) -> bool:
        with self.lock:
            return self.storage.pop(url, None) is not None

    def clear(self) -> int:
        with self.lock:
            n = len(self.storage)
            self.storage.clear()
            return n