"""Cache factory + invalidation helpers.

`cache` is a module-level singleton chosen at import time based on
`config['cache_type']`. The dashboard can call `invalidate(url)` to drop
a single entry.
"""
from cache.lru_cache import LRUCache
from cache.memory_cache import MemoryCache
from cache.redis_cache import RedisCache
from proxy.config import config


def get_cache_instance():
    cache_type = (config.get("cache_type") or "memory").lower()
    ttl = int(config.get("cache_ttl", 300))
    if cache_type == "redis":
        rc = config.get("redis", {}) or {}
        return RedisCache(
            ttl=ttl,
            host=rc.get("host", "localhost"),
            port=int(rc.get("port", 6379)),
            db=int(rc.get("db", 0)),
            password=rc.get("password"),
        )
    if cache_type == "lru":
        return LRUCache(ttl=ttl, max_size=int(config.get("cache_max_size", 100)))
    return MemoryCache(ttl=ttl)


cache = get_cache_instance()


def invalidate(url: str) -> bool:
    """Remove a single URL from the cache. Returns True if it existed."""
    if not url:
        return False
    return cache.delete(url)


def flush_all() -> int:
    """Drop every entry. Returns the number removed (best-effort)."""
    return cache.clear()