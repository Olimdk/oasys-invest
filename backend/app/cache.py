"""Tiny TTL cache so the app stays fast and resilient to API rate limits."""

from __future__ import annotations

import time
from functools import wraps


def ttl_cache(ttl: float = 600):
    """Memoize fn results for `ttl` seconds (per-argument-keyed)."""

    def decorator(fn):
        store: dict = {}

        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            hit = store.get(key)
            if hit and now - hit[1] < ttl:
                return hit[0]
            val = fn(*args, **kwargs)
            store[key] = (val, now)
            return val

        wrapper.cache_clear = store.clear
        return wrapper

    return decorator
