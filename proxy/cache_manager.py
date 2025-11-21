# proxy/cache_manager.py

import json
from cache.memory_cache import MemoryCache
from cache.redis_cache import RedisCache

def get_cache_instance():
    with open("config.json", "r") as f:
        config = json.load(f)

    cache_type = config.get("cache_type", "memory")
    ttl = config.get("cache_ttl", 300)

    if cache_type == "redis":
        redis_config = config.get("redis", {})
        return RedisCache(
            ttl=ttl,
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
        )
    else: # memory is default
        return MemoryCache(ttl=ttl)

# Create a global instance to be used by the proxy and dashboard
cache = get_cache_instance()