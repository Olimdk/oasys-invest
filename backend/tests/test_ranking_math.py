"""Unit tests for the pure scoring + performance math (no network)."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ranking import skyrocket_score, performance_stats


def _report(**over):
    base = {
        "signal": {"action": "BUY", "score": 4, "confidence": "high", "reasons": []},
        "indicators": {"sma50": 185.0, "sma200": 170.0, "rsi": 55.0, "last_close": 190.0},
        "valuation": {"earnings_growth": 0.2, "revenue_growth": 0.15},
        "range_52w": {"position_pct": 20.0},
        "analyst": {"target_mean": 240.0},
        "quote": {"price": 190.0},
    }
    base.update(over)
    return base


def test_score_in_range_and_graded():
    s = skyrocket_score(_report())
    assert 0 <= s["score"] <= 100
    assert s["grade"] in {"A", "B", "C", "D", "F"}
    assert s["action"] == "BUY"


def test_uptrend_and_growth_boost_score():
    strong = skyrocket_score(_report(
        indicators={"sma50": 185.0, "sma200": 170.0, "rsi": 55.0, "last_close": 190.0},
        valuation={"earnings_growth": 0.5, "revenue_growth": 0.5},
        analyst={"target_mean": 400.0}, quote={"price": 190.0}))
    weak = skyrocket_score(_report(
        indicators={"sma50": 95.0, "sma200": 100.0, "rsi": 75.0, "last_close": 90.0},
        valuation={"earnings_growth": 0.0, "revenue_growth": 0.0},
        analyst={"target_mean": 70.0}, quote={"price": 90.0},
        range_52w={"position_pct": 95.0}, signal={"action": "SELL", "score": -4, "confidence": "low", "reasons": []}))
    assert strong["score"] > weak["score"]


def test_performance_stats_from_chart():
    chart = [{"close": 100.0}, {"close": 120.0}, {"close": 90.0}, {"close": 110.0}]
    stats = performance_stats(chart)
    assert stats["return_1y_pct"] == 10.0          # (110-100)/100
    assert stats["max_drawdown_pct"] == 25.0        # (120-90)/120
    assert stats["points"] == 4


def test_performance_stats_empty():
    assert performance_stats([])["points"] == 0
    assert performance_stats(None)["points"] == 0
