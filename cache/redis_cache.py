"""Redis-backed cache. Falls back to MemoryCache if Redis is unreachable."""
import threading

import redis

from cache.memory_cache import MemoryCache


class RedisCache:
    def __init__(self, ttl=300, host="localhost", port=6379, db=0, password=None):
        self.ttl = int(ttl)
        self._lock = threading.Lock()
        self._fallback = None
        self.client = None
        try:
            self.client = redis.Redis(
                host=host, port=int(port), db=int(db),
                password=password, decode_responses=False,
                socket_connect_timeout=2, socket_timeout=2,
            )
            self.client.ping()
            print("[cache:redis] connected to", host, port)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError, OSError) as e:
            print(f"[cache:redis] could not connect ({e}); falling back to in-memory cache")
            self._fallback = MemoryCache(ttl=self.ttl)

    def _backend(self):
        return self._fallback if self._fallback is not None else self

    def set(self, url, content):
        with self._lock:
            if self._fallback is not None:
                self._fallback.set(url, content)
                return
            try:
                self.client.setex(url, self.ttl, content)
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                self._fallback = MemoryCache(ttl=self.ttl)
                self._fallback.set(url, content)

    def get(self, url):
        with self._lock:
            if self._fallback is not None:
                return self._fallback.get(url)
            try:
                return self.client.get(url)
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                self._fallback = MemoryCache(ttl=self.ttl)
                return None

    def keys(self):
        with self._lock:
            if self._fallback is not None:
                return self._fallback.keys()
            try:
                return [k.decode() if isinstance(k, bytes) else k for k in self.client.keys("*")]
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                self._fallback = MemoryCache(ttl=self.ttl)
                return []

    def size(self):
        with self._lock:
            if self._fallback is not None:
                return self._fallback.size()
            try:
                return int(self.client.dbsize())
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                self._fallback = MemoryCache(ttl=self.ttl)
                return 0

    def delete(self, url) -> bool:
        with self._lock:
            if self._fallback is not None:
                return self._fallback.delete(url)
            try:
                return bool(self.client.delete(url))
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                self._fallback = MemoryCache(ttl=self.ttl)
                return False

    def clear(self) -> int:
        with self._lock:
            if self._fallback is not None:
                return self._fallback.clear()
            try:
                # dbsize before flush, then flush
                n = int(self.client.dbsize())
                self.client.flushdb()
                return n
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                self._fallback = MemoryCache(ttl=self.ttl)
                return 0
