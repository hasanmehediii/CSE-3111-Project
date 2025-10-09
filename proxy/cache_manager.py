# proxy/cache_manager.py

import time

class CacheManager:
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
        return list(self.storage.keys())

    def size(self):
        return len(self.storage)


# ✅ Create a global instance to import from dashboard
cache = CacheManager()
