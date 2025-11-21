# cache/redis_cache.py

import redis

class RedisCache:
    def __init__(self, ttl=300, host='localhost', port=6379):
        self.ttl = ttl
        try:
            self.client = redis.Redis(host=host, port=port, db=0, decode_responses=True)
            self.client.ping()
            print("✅ Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            print(f"❌ Could not connect to Redis: {e}")
            print("⚠️ Falling back to in-memory cache.")
            # Fallback to memory cache if Redis is not available
            from .memory_cache import MemoryCache
            self.__class__ = MemoryCache # Replace this instance's class with MemoryCache
            self.__init__(ttl=ttl)


    def set(self, url, content):
        self.client.setex(url, self.ttl, content)

    def get(self, url):
        return self.client.get(url)

    def keys(self):
        return self.client.keys('*')

    def size(self):
        return self.client.dbsize()

    def clear(self):
        self.client.flushdb()
