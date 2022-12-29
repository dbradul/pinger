import threading

import ratelimit


class ScopeRateLimiter:
    def __init__(self, **kwargs):
        self.config = kwargs
        self.scopes = {}

    def check_limits(self, scope):
        result = True
        if scope not in self.scopes:
            self.scopes[scope] = ratelimit.limits(**self.config)(lambda: None)
        try:
            self.scopes[scope]()
        except ratelimit.exception.RateLimitException as e:
            result = False
        return result


class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance