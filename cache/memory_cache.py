# cache/memory_cache.py

import time

class MemoryCache:
    def __init__(self, ttl=300):
        self.storage = {}
        self.ttl = ttl  # time to live in seconds

    def set(self, url, content):
        self.storage[url] = {"content": content, "timestamp": time.time()}

    def get(self, url):
        data = self.storage.get(url)
        if not data:
            return None
        # check if expired
        if time.time() - data["timestamp"] > self.ttl:
            del self.storage[url]
            return None
        return data["content"]

    def keys(self):
        # Prune expired keys before returning
        now = time.time()
        expired_keys = [
            k for k, v in self.storage.items() if now - v["timestamp"] > self.ttl
        ]
        for k in expired_keys:
            del self.storage[k]
        return list(self.storage.keys())

    def size(self):
        # Prune expired keys before returning size
        now = time.time()
        expired_keys = [
            k for k, v in self.storage.items() if now - v["timestamp"] > self.ttl
        ]
        for k in expired_keys:
            del self.storage[k]
        return len(self.storage)

    def clear(self):
        self.storage.clear()