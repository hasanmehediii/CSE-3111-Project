"""Thread-safe LRU cache with TTL and per-key invalidation."""
import time
import threading
from collections import OrderedDict


class LRUCache:
    def __init__(self, ttl=300, max_size=100):
        self.ttl = ttl
        self.max_size = max_size
        self.storage = OrderedDict()
        self.lock = threading.Lock()

    def _prune_expired(self):
        now = time.time()
        expired = [k for k, v in self.storage.items() if now - v["timestamp"] > self.ttl]
        for k in expired:
            del self.storage[k]

    def get(self, url):
        with self.lock:
            data = self.storage.get(url)
            if not data:
                return None
            if time.time() - data["timestamp"] > self.ttl:
                del self.storage[url]
                return None
            self.storage.move_to_end(url)
            return data["content"]

    def set(self, url, content):
        with self.lock:
            now = time.time()
            if url in self.storage:
                self.storage[url] = {"content": content, "timestamp": now}
                self.storage.move_to_end(url)
                return
            while len(self.storage) >= self.max_size:
                self.storage.popitem(last=False)
            self.storage[url] = {"content": content, "timestamp": now}

    def keys(self):
        with self.lock:
            self._prune_expired()
            return list(self.storage.keys())

    def size(self):
        with self.lock:
            self._prune_expired()
            return len(self.storage)

    def delete(self, url) -> bool:
        with self.lock:
            return self.storage.pop(url, None) is not None

    def clear(self) -> int:
        with self.lock:
            n = len(self.storage)
            self.storage.clear()
            return n
