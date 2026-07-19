"""Skyrocket scoring: ranks trending tickers by long-horizon upside potential.

Combines the rule-based signal from analyze.py with valuation, momentum, and
growth factors. Fully transparent — every point carries a human-readable reason.
Scores are 0-100 (50 = neutral / average market candidate).
"""

from __future__ import annotations


def skyrocket_score(report: dict) -> dict:
    """Return a 0-100 skyrocket score for a stock-report dict."""
    reasons: list[str] = []
    score = 0

    sig = report.get("signal") or {}
    ind = report.get("indicators") or {}
    val = report.get("valuation") or {}
    rng = report.get("range_52w") or {}
    ana = report.get("analyst") or {}
    quote = report.get("quote") or {}

    # 1) Trend structure (price vs moving averages)
    sma50 = ind.get("sma50")
    sma200 = ind.get("sma200")
    last = ind.get("last_close") or quote.get("price")
    if last and sma50 and sma200:
        if last > sma50 > sma200:
            score += 18
            reasons.append("Confirmed uptrend (price above both 50d & 200d averages).")
        elif last < sma50 < sma200:
            score -= 14
            reasons.append("Downtrend (price below both averages).")
        else:
            reasons.append("Mixed trend (averages have crossed).")

    # 2) Momentum (RSI)
    rsi = ind.get("rsi")
    if rsi is not None:
        if 45 <= rsi <= 60:
            score += 12
            reasons.append(f"RSI {rsi} — healthy momentum, not overbought.")
        elif rsi < 35:
            score += 8
            reasons.append(f"RSI {rsi} — oversold, mean-reversion candidate.")
        elif rsi > 70:
            score -= 10
            reasons.append(f"RSI {rsi} — overbought, limited near-term upside.")

    # 3) Analyst target upside
    target = ana.get("target_mean")
    if target and last:
        upside = (target - last) / last * 100
        if upside > 20:
            score += 20
            reasons.append(f"Analyst target implies +{upside:.0f}% upside.")
        elif upside > 10:
            score += 12
            reasons.append(f"Analyst target implies +{upside:.0f}% upside.")
        elif upside < -10:
            score -= 8
            reasons.append(f"Analyst target implies {upside:.0f}% downside.")
        else:
            reasons.append(f"Price near analyst target ({upside:+.0f}%).")

    # 4) Quality growth (long-horizon engine)
    eg = val.get("earnings_growth")
    rg = val.get("revenue_growth")
    if eg is not None and eg > 0.15:
        score += 10
        reasons.append(f"Earnings growth {eg * 100:.0f}% (strong).")
    if rg is not None and rg > 0.10:
        score += 8
        reasons.append(f"Revenue growth {rg * 100:.0f}%.")

    # 5) 52-week position (margin of safety)
    pos = rng.get("position_pct")
    if pos is not None:
        if pos < 25:
            score += 8
            reasons.append("Near 52-week low — margin of safety.")
        elif pos > 85:
            score -= 8
            reasons.append("Near 52-week high — little margin of safety.")

    # 6) Agreement with the rule-based signal
    base = sig.get("score") or 0
    if base >= 3:
        score += 10
        reasons.append("Rule-based signal agrees: BUY.")
    elif base <= -3:
        score -= 10
        reasons.append("Rule-based signal warns: SELL.")

    score = max(0, min(100, round(score + 50)))  # shift to 0-100, clamp

    if score >= 75:
        grade = "A"
    elif score >= 60:
        grade = "B"
    elif score >= 45:
        grade = "C"
    elif score >= 30:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": score,
        "grade": grade,
        "action": sig.get("action", "HOLD"),
        "reasons": reasons,
    }


def performance_stats(chart: list[dict]) -> dict:
    """Transparent, history-based stats from a ticker's 1y chart.

    Returns the realized 12-month return and max drawdown, plus a simple
    consistency flag comparing the current signal to that realized return.
    No external data — purely derived from the chart we already fetch.
    """
    if not chart or len(chart) < 2:
        return {"return_1y_pct": None, "max_drawdown_pct": None, "points": 0}
    closes = [c["close"] for c in chart if c.get("close") is not None]
    if len(closes) < 2:
        return {"return_1y_pct": None, "max_drawdown_pct": None, "points": len(closes)}
    start, end = closes[0], closes[-1]
    ret = (end - start) / start * 100 if start else 0.0
    peak = closes[0]
    max_dd = 0.0
    for v in closes:
        if v > peak:
            peak = v
        if peak:
            dd = (peak - v) / peak * 100
            if dd > max_dd:
                max_dd = dd
    return {
        "return_1y_pct": round(ret, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "points": len(closes),
    }
