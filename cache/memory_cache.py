import time

class MemoryCache:
    def __init__(self, ttl=300):
        self.ttl = ttl
        self.cache = {}

    def get(self, key):
        item = self.cache.get(key)
        if item and (time.time() - item["time"]) < self.ttl:
            return item["data"]
        elif item:
            del self.cache[key]
        return None

    def set(self, key, data):
        self.cache[key] = {"data": data, "time": time.time()}

    def all_keys(self):
        return list(self.cache.keys())
