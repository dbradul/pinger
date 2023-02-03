import threading
from typing import Dict, Any

import ratelimit
from enum import Enum


class TextStyle(Enum):
    BOLD = 1
    ITALIC = 2
    UNDERLINE = 3
    CODE = 4


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

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
                    cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


class ThreadSafeSingleton(type):
    _instances = {}
    _singleton_locks: Dict[Any, threading.Lock] = {}

    def __call__(cls, *args, **kwargs):
        # double-checked locking pattern (https://en.wikipedia.org/wiki/Double-checked_locking)
        if cls not in cls._instances:
            if cls not in cls._singleton_locks:
                cls._singleton_locks[cls] = threading.Lock()
            with cls._singleton_locks[cls]:
                if cls not in cls._instances:
                    cls._instances[cls] = super(ThreadSafeSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]