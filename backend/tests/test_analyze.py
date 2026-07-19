"""Tests for indicators and the buy/hold/sell signal."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

from analyze import sma, rsi, compute_indicators, price_vs_moving_averages, signal


def test_sma_basic():
    v = [1, 2, 3, 4, 5]
    out = sma(v, 3)
    assert out[0] is None and out[1] is None
    assert out[2] == 2.0 and out[4] == 4.0


def test_rsi_rising_is_100():
    v = list(range(1, 30))
    assert rsi(v, 14)[-1] == 100.0


def test_rsi_falling_is_0():
    v = list(range(30, 1, -1))
    assert rsi(v, 14)[-1] == 0.0


def test_compute_indicators():
    closes = list(range(1, 210))
    vols = [1000] * len(closes)
    ind = compute_indicators(closes, vols)
    assert ind["sma200"] is not None and ind["sma50"] is not None and ind["rsi"] is not None


def test_trend_classification():
    assert price_vs_moving_averages(120, 110, 100) == "uptrend"
    assert price_vs_moving_averages(80, 100, 110) == "downtrend"
    assert price_vs_moving_averages(105, 110, 100) == "mixed"


def test_signal_buy_strong_uptrend():
    s = signal(120, 110, 108, 100, 60, 30, 140, 90, 130)
    assert s["action"] == "BUY" and s["score"] >= 3


def test_signal_sell_strong_downtrend():
    s = signal(80, 100, 102, 110, 75, 50, 70, 75, 130)
    assert s["action"] == "SELL" and s["score"] <= -3


def test_signal_hold_middle():
    s = signal(105, 110, 109, 100, 50, 30, 106, 90, 130)
    assert s["action"] == "HOLD"
