"""Technical indicators + a transparent buy/hold/sell signal (heuristic, not a black box)."""

from __future__ import annotations


def sma(values: list[float], window: int) -> list[float]:
    out = [None] * len(values)
    for i in range(window - 1, len(values)):
        out[i] = round(sum(values[i - window + 1 : i + 1]) / window, 2)
    return out


def rsi(values: list[float], period: int = 14) -> list[float]:
    out = [None] * len(values)
    if len(values) <= period:
        return out
    gains, losses = [], []
    for i in range(1, len(values)):
        d = values[i] - values[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    out[period] = _rsi_val(avg_gain, avg_loss)
    for i in range(period + 1, len(values)):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        out[i] = _rsi_val(avg_gain, avg_loss)
    return out


def _rsi_val(avg_gain, avg_loss):
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def compute_indicators(closes: list[float], volumes: list[float]):
    ma50 = sma(closes, 50)
    ma200 = sma(closes, 200)
    r = rsi(closes, 14)
    return {
        "sma50": ma50[-1] if (ma50 and ma50[-1] is not None) else None,
        "sma200": ma200[-1] if (ma200 and ma200[-1] is not None) else None,
        "rsi": r[-1] if (r and r[-1] is not None) else None,
        "last_close": closes[-1] if closes else None,
    }


def price_vs_moving_averages(last_close, sma50, sma200):
    if sma50 is None or sma200 is None:
        return "unknown"
    if last_close > sma50 > sma200:
        return "uptrend"
    if last_close < sma50 < sma200:
        return "downtrend"
    return "mixed"


def signal(last_close, sma50, sma50_prev, sma200, rsi, pe, target_price,
           fifty_two_week_low, fifty_two_week_high) -> dict:
    reasons = []
    score = 0
    trend = price_vs_moving_averages(last_close, sma50, sma200)
    if trend == "uptrend":
        score += 2
        reasons.append("Price above both 50d & 200d averages (uptrend).")
    elif trend == "downtrend":
        score -= 2
        reasons.append("Price below both 50d & 200d averages (downtrend).")
    else:
        reasons.append("Price vs averages is mixed (crossed/unclear).")

    if sma50 is not None and sma50_prev is not None:
        if sma50 > sma50_prev:
            score += 1
            reasons.append("50-day average is rising.")
        else:
            score -= 1
            reasons.append("50-day average is falling.")

    if rsi is not None:
        if rsi < 30:
            score += 2
            reasons.append(f"RSI {rsi} — oversold (mean-reversion candidate).")
        elif rsi > 70:
            score -= 2
            reasons.append(f"RSI {rsi} — overbought (caution).")
        elif rsi < 45:
            score -= 1
            reasons.append(f"RSI {rsi} — weak momentum.")
        elif rsi > 55:
            score += 1
            reasons.append(f"RSI {rsi} — healthy momentum.")

    if target_price is not None and last_close:
        upside = (target_price - last_close) / last_close * 100
        if upside > 8:
            score += 1
            reasons.append(f"Analyst mean target implies +{upside:.1f}% upside.")
        elif upside < -8:
            score -= 1
            reasons.append(f"Analyst mean target implies {upside:.1f}% downside.")
        else:
            reasons.append(f"Price near analyst target ({upside:+.1f}%).")

    if fifty_two_week_low and fifty_two_week_high and last_close:
        pos = (last_close - fifty_two_week_low) / (fifty_two_week_high - fifty_two_week_low)
        if pos > 0.9:
            score -= 1
            reasons.append("Near 52-week high (limited margin of safety).")
        elif pos < 0.1:
            score += 1
            reasons.append("Near 52-week low (potential value).")

    if score >= 3:
        action = "BUY"
    elif score <= -3:
        action = "SELL"
    else:
        action = "HOLD"
    return {
        "action": action,
        "score": score,
        "confidence": "high" if abs(score) >= 4 else "moderate" if abs(score) >= 2 else "low",
        "reasons": reasons,
    }
