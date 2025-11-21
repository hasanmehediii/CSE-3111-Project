# proxy/request_log.py

import threading
from collections import deque

class RequestLog:
    def __init__(self, max_size=100):
        self.log = deque(maxlen=max_size)
        self.lock = threading.Lock()

    def add(self, entry):
        with self.lock:
            self.log.appendleft(entry)

    def get_all(self):
        with self.lock:
            return list(self.log)

# Global instance for request logging
request_log = RequestLog()
