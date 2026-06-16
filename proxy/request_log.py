"""Thread-safe in-memory request log (ring buffer)."""
import threading
from collections import deque


class RequestLog:
    def __init__(self, max_size=200):
        self.log = deque(maxlen=max_size)
        self.lock = threading.Lock()

    def add(self, entry):
        with self.lock:
            self.log.appendleft(entry)

    def get_all(self):
        with self.lock:
            return list(self.log)

    def clear_for_url(self, url):
        with self.lock:
            self.log = deque(
                [e for e in self.log if e.get("url") != url],
                maxlen=self.log.maxlen,
            )

    def get_latest_for_url(self, url):
        with self.lock:
            for entry in self.log:
                if entry.get("url") == url:
                    return entry
            return None

    def clear_all(self):
        with self.lock:
            self.log.clear()


request_log = RequestLog()
