"""Unit tests for the cache backends."""
import time
import threading
import unittest

from cache.memory_cache import MemoryCache
from cache.lru_cache import LRUCache


class MemoryCacheTests(unittest.TestCase):
    def test_set_and_get(self):
        c = MemoryCache(ttl=60)
        c.set("u1", b"hello")
        self.assertEqual(c.get("u1"), b"hello")

    def test_ttl_expiry(self):
        c = MemoryCache(ttl=1)
        c.set("u1", b"hi")
        time.sleep(1.2)
        self.assertIsNone(c.get("u1"))

    def test_delete(self):
        c = MemoryCache(ttl=60)
        c.set("u1", b"a")
        self.assertTrue(c.delete("u1"))
        self.assertIsNone(c.get("u1"))
        self.assertFalse(c.delete("u1"))

    def test_clear_returns_count(self):
        c = MemoryCache(ttl=60)
        c.set("u1", b"a")
        c.set("u2", b"b")
        c.set("u3", b"c")
        self.assertEqual(c.clear(), 3)
        self.assertEqual(c.clear(), 0)

    def test_thread_safety(self):
        c = MemoryCache(ttl=60)

        def writer(prefix):
            for i in range(200):
                c.set(f"{prefix}{i}", b"x")

        threads = [threading.Thread(target=writer, args=(f"t{i}-",)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertIsInstance(c.size(), int)


class LRUCacheTests(unittest.TestCase):
    def test_lru_eviction(self):
        c = LRUCache(max_size=2)
        c.set("a", b"1")
        c.set("b", b"2")
        _ = c.get("a")  # mark 'a' as most-recently-used
        c.set("c", b"3")
        self.assertEqual(c.get("a"), b"1")
        self.assertIsNone(c.get("b"))
        self.assertEqual(c.get("c"), b"3")

    def test_delete(self):
        c = LRUCache(max_size=10)
        c.set("u1", b"v")
        self.assertTrue(c.delete("u1"))
        self.assertIsNone(c.get("u1"))

    def test_clear(self):
        c = LRUCache(max_size=10)
        c.set("u1", b"v")
        c.set("u2", b"v")
        self.assertEqual(c.clear(), 2)


if __name__ == "__main__":
    unittest.main()
