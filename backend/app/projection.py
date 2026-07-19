"""Forward projection (engine prediction).

A transparent, assumption-disclosed projection of probable price range over a
horizon. Uses a simple drift (recent slope) + volatility cone. NOT a guarantee;
clearly a heuristic scenario, not financial advice.
"""

from __future__ import annotations

from .ranking import performance_stats


def _slope(closes):
    n = len(closes)
    if n < 2:
        return 0.0
    # ordinary least squares slope per bar
    x = list(range(n))
    mx = sum(x) / n
    my = sum(closes) / n
    num = sum((x[i] - mx) * (closes[i] - my) for i in range(n))
    den = sum((x[i] - mx) ** 2 for i in range(n))
    return num / den if den else 0.0


def _stdev(closes):
    n = len(closes)
    if n < 2:
        return 0.0
    m = sum(closes) / n
    return (sum((c - m) ** 2 for c in closes) / n) ** 0.5


def project(report: dict, horizon_bars: int = 21, mode: str = "long") -> dict:
    """Return a projection dict: expected, bull, bear, method notes."""
    chart = report.get("chart") or []
    closes = [c["close"] for c in chart if c.get("close") is not None]
    notes = []
    if len(closes) < 10:
        return {"expected": None, "bull": None, "bear": None,
                "horizon_bars": horizon_bars, "method": "insufficient history",
                "notes": ["Not enough price history to project."]}
    last = closes[-1]
    slope = _slope(closes)
    sd = _stdev(closes)
    # For daytrade mode, dampen drift and tighten to recent volatility.
    if mode == "daytrade":
        drift = slope * horizon_bars * 0.5
        band = sd * 1.0
        notes.append("Intraday/swing drift (half-weight) + 1σ band.")
    else:
        drift = slope * horizon_bars
        band = sd * 1.5
        notes.append("Trend drift (OLS slope) + 1.5σ band.")
    expected = last + drift
    bull = expected + band
    bear = max(0.01, expected - band)
    stats = performance_stats(chart)
    notes.append(f"Realized 1y return {stats.get('return_1y_pct')}% (for context).")
    return {
        "last": round(last, 2),
        "expected": round(expected, 2),
        "bull": round(bull, 2),
        "bear": round(bear, 2),
        "horizon_bars": horizon_bars,
        "mode": mode,
        "method": "OLS drift + volatility cone",
        "notes": notes,
    }
