"""Centralized configuration loader.

All modules should import `config` from here instead of re-reading config.json.
"""
import json
import threading


class AppConfig:
    """Thread-safe wrapper around config.json.

    The proxy can reload config at runtime (e.g., when the user edits
    config.json from the dashboard). Reads use a lock so partial writes
    don't tear the dict.
    """

    DEFAULTS = {
        "proxy_port": 8080,
        "dashboard_port": 5000,
        "cache_type": "memory",
        "cache_ttl": 300,
        "cache_max_size": 100,
        "redis": {"host": "localhost", "port": 6379},
        "proxy_user": None,
        "proxy_password": None,
        "blacklist": [],
        "content_blacklist": [],
        "retries": {"total": 3, "backoff_factor": 0.5},
        "bind_host": "0.0.0.0",
        "request_timeout": 15,
    }

    def __init__(self, path="config.json"):
        self._path = path
        self._lock = threading.RLock()
        self._data = {}
        self.reload()

    def reload(self):
        with self._lock:
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            except FileNotFoundError:
                raw = {}
            merged = dict(self.DEFAULTS)
            merged.update(raw)
            # Merge nested dicts (redis, retries)
            for key in ("redis", "retries"):
                if key in raw and isinstance(raw[key], dict):
                    sub = dict(self.DEFAULTS[key])
                    sub.update(raw[key])
                    merged[key] = sub
            self._data = merged

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def all(self):
        with self._lock:
            return dict(self._data)


# Module-level singleton imported by other modules
config = AppConfig()
