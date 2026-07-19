"""Short-term / daytrading skyrocket scoring & recommendation.

Implements a fast, transparent signal for intraday & swing horizons, grounded
in the user's Obsidian Trading notes (RSI extremes, MACD, Bollinger breakout,
volume-supported momentum, volatility expansion). Scores 0-100 (50 = neutral).

Refinements (v2):
- Bollinger %B for precise band position
- RSI zone labeling (oversold / momentum / overbought)
- Volatility regime via recent ATR-style range
- Explicit BUY/SELL/HOLD mapping with confidence
Every point carries a human-readable reason.
"""

from __future__ import annotations


def _sma(vals, n):
    if len(vals) < n:
        return None
    return sum(vals[-n:]) / n


def _std(vals, n):
    if len(vals) < n:
        return None
    m = sum(vals[-n:]) / n
    return (sum((v - m) ** 2 for v in vals[-n:]) / n) ** 0.5


def _ema(series, span):
    if len(series) < span:
        return None
    k = 2 / (span + 1)
    out = [series[0]]
    for v in series[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def _rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    gains = losses = 0.0
    for i in range(-n, 0):
        d = closes[i] - closes[i - 1]
        gains += max(d, 0.0)
        losses += max(-d, 0.0)
    if losses == 0:
        return 100.0
    rs = (gains / n) / (losses / n)
    return 100 - (100 / (1 + rs))


def _macd(closes):
    if len(closes) < 35:
        return None, None
    fast = _ema(closes, 12)
    slow = _ema(closes, 26)
    if fast is None or slow is None:
        return None, None
    line = fast[-1] - slow[-1]
    sig = _ema([fast[i] - slow[i] for i in range(len(fast))], 9)
    return line, (sig[-1] if sig else None)


def daytrade_score(report: dict) -> dict:
    """Return a 0-100 short-horizon score for a stock-report dict."""
    reasons: list[str] = []
    score = 0
    chart = report.get("chart") or []
    closes = [c["close"] for c in chart if c.get("close") is not None]
    vols = [c.get("volume", 0) for c in chart]
    last = (report.get("quote") or {}).get("price")

    if not closes:
        ind = report.get("indicators") or {}
        last = last or ind.get("last_close")
        rsi = ind.get("rsi")
        if rsi is not None and 40 <= rsi <= 65:
            score += 12
            reasons.append(f"RSI {rsi:.0f} — healthy momentum (limited data).")
    else:
        rsi = _rsi(closes)
        sma20 = _sma(closes, 20)
        sma50 = _sma(closes, 50)
        sd20 = _std(closes, 20)
        macd_line, macd_sig = _macd(closes)
        avg_vol = (sum(vols[-20:]) / 20) if len(vols) >= 20 else (sum(vols) / len(vols) if vols else 0)
        recent_vol = vols[-1] if vols else 0
        # ATR-style volatility (range of last 10 closes)
        atr = (_std(closes[-10:], 10) or 0) / (last or 1)

        if rsi is not None:
            if 45 <= rsi <= 65:
                score += 18; reasons.append(f"RSI {rsi:.0f} — strong intraday momentum, not exhausted.")
            elif rsi < 32:
                score += 12; reasons.append(f"RSI {rsi:.0f} — oversold bounce candidate.")
            elif rsi > 76:
                score -= 12; reasons.append(f"RSI {rsi:.0f} — overbought, fade risk.")

        if macd_line is not None and macd_sig is not None:
            if macd_line > macd_sig:
                score += 16; reasons.append("MACD above signal — bullish momentum trigger.")
            else:
                score -= 10; reasons.append("MACD below signal — bearish momentum.")

        if sma20 and sd20:
            upper, lower = sma20 + 2 * sd20, sma20 - 2 * sd20
            pctb = (last - lower) / (upper - lower) if upper > lower else 0.5
            if pctb > 1.0:
                score += 14; reasons.append("Price breaking upper Bollinger — volatility expansion.")
            elif pctb < 0.0:
                score += 8; reasons.append("Price at lower band — mean-reversion long setup.")
            elif abs(pctb - 0.5) < 0.05:
                score -= 4; reasons.append("Price pinned to mid-band — no edge yet.")

        if avg_vol and recent_vol > avg_vol * 1.5:
            score += 12; reasons.append("Volume 1.5x average — conviction behind move.")
        elif avg_vol and recent_vol < avg_vol * 0.6:
            score -= 6; reasons.append("Thin volume — weak conviction.")

        if sma20 and sma50:
            if sma20 > sma50:
                score += 10; reasons.append("20-period avg above 50 — uptrending structure.")
            else:
                score -= 8; reasons.append("20-period avg below 50 — downtrending.")

        if atr > 0.03:
            reasons.append(f"High volatility regime (ATR ~{atr*100:.0f}%) — size positions small.")

    score = max(0, min(100, round(score + 50)))
    grade = ("A" if score >= 75 else "B" if score >= 60 else "C" if score >= 45
             else "D" if score >= 30 else "F")
    action = "BUY" if score >= 60 else "SELL" if score <= 35 else "HOLD"
    confidence = "high" if abs(score - 50) >= 18 else "moderate" if abs(score - 50) >= 8 else "low"
    return {"score": score, "grade": grade, "action": action, "confidence": confidence,
            "reasons": reasons, "mode": "daytrade"}
