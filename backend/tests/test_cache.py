"""Tests for the TTL cache used by market data calls."""

import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.cache import ttl_cache


def test_cache_returns_same_value_and_caches():
    calls = {"n": 0}

    @ttl_cache(ttl=5)
    def f(x):
        calls["n"] += 1
        return x * 2

    assert f(2) == 4
    assert f(2) == 4          # cached, no extra call
    assert calls["n"] == 1


def test_cache_expires_after_ttl():
    calls = {"n": 0}

    @ttl_cache(ttl=1)
    def g():
        calls["n"] += 1
        return calls["n"]

    first = g()
    assert first == 1
    time.sleep(1.1)
    second = g()
    assert second == 2        # cache expired, recomputed
    assert calls["n"] == 2
