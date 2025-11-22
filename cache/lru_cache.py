# cache/lru_cache.py
import time
from collections import OrderedDict
import threading

class LRUCache:
    def __init__(self, ttl=300, max_size=100):
        self.ttl = ttl
        self.max_size = max_size
        self.storage = OrderedDict()
        self.lock = threading.Lock()

    def get(self, url):
        with self.lock:
            data = self.storage.get(url)
            if not data:
                return None

            # Check for expiration
            if time.time() - data["timestamp"] > self.ttl:
                del self.storage[url]
                return None
            
            # Move to the end to mark as recently used
            self.storage.move_to_end(url)
            return data["content"]

    def set(self, url, content):
        with self.lock:
            if url in self.storage:
                # Update existing entry and move to end
                self.storage[url] = {"content": content, "timestamp": time.time()}
                self.storage.move_to_end(url)
            else:
                # Evict if full
                if len(self.storage) >= self.max_size:
                    self.storage.popitem(last=False)  # Pop least recently used
                
                self.storage[url] = {"content": content, "timestamp": time.time()}

    def keys(self):
        with self.lock:
            self._prune_expired()
            return list(self.storage.keys())

    def size(self):
        with self.lock:
            self._prune_expired()
            return len(self.storage)

    def clear(self):
        with self.lock:
            self.storage.clear()

    def _prune_expired(self):
        # This must be called within a lock
        now = time.time()
        expired_keys = [
            k for k, v in self.storage.items() if now - v["timestamp"] > self.ttl
        ]
        for k in expired_keys:
            del self.storage[k]
