"""Market data core for the Investor app (yfinance-backed)."""

from __future__ import annotations

import yfinance as yf

from .analyze import compute_indicators, signal, sma
from .cache import ttl_cache


@ttl_cache(ttl=600)
def _ticker(symbol: str):
    return yf.Ticker(symbol)


@ttl_cache(ttl=120)
def get_quote(symbol: str) -> dict:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("symbol must not be empty")
    t = _ticker(symbol)
    hist = t.history(period="5d")
    if hist is None or len(hist) == 0:
        raise ValueError(f"No data for symbol {symbol!r}")
    closes = hist["Close"]
    last = float(closes.iloc[-1])
    prev = float(closes.iloc[-2]) if len(closes) > 1 else last
    change = last - prev
    pct = (change / prev) * 100 if prev else 0.0
    as_of = closes.index[-1]
    as_of_str = as_of.strftime("%Y-%m-%d") if hasattr(as_of, "strftime") else str(as_of)
    return {
        "symbol": symbol, "price": round(last, 2), "previous_close": round(prev, 2),
        "change": round(change, 2), "change_percent": round(pct, 2), "as_of": as_of_str,
    }


@ttl_cache(ttl=300)
def get_history(symbol: str, period: str = "1mo") -> list[dict]:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("symbol must not be empty")
    t = _ticker(symbol)
    hist = t.history(period=period)
    if hist is None or len(hist) == 0:
        raise ValueError(f"No data for symbol {symbol!r}")
    out = []
    for idx, row in hist.iterrows():
        d = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)
        out.append({"date": d, "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]) if "Volume" in row else 0})
    return out


@ttl_cache(ttl=1800)
def get_quotes(symbols: list[str]) -> list[dict]:
    return [get_quote(s) for s in symbols]


@ttl_cache(ttl=1800)
def get_stock_report(symbol: str, period: str = "1y") -> dict:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("symbol must not be empty")
    t = _ticker(symbol)
    hist = t.history(period=period)
    if hist is None or len(hist) == 0:
        raise ValueError(f"No data for symbol {symbol!r}")

    closes = [float(x) for x in hist["Close"]]
    volumes = [int(x) for x in hist["Volume"]]
    last = closes[-1]
    prev = closes[-2] if len(closes) > 1 else last
    change = last - prev
    pct = (change / prev) * 100 if prev else 0.0

    info = {}
    try:
        info = t.info or {}
    except Exception:
        info = {}

    domain = ""
    website = info.get("website") or ""
    if website:
        domain = website.replace("https://", "").replace("http://", "").rstrip("/").split("/")[0]
    logo_url = f"https://logo.clearbit.com/{domain}" if domain else ""

    ind = compute_indicators(closes, volumes)
    sma50_series = sma(closes, 50)
    sma50_prev = None
    for v in reversed(sma50_series[:-1]):
        if v is not None:
            sma50_prev = v
            break

    sig = signal(last, ind["sma50"], sma50_prev, ind["sma200"], ind["rsi"],
                 info.get("trailingPE"), info.get("targetMeanPrice"),
                 info.get("fiftyTwoWeekLow"), info.get("fiftyTwoWeekHigh"))

    step = max(1, len(closes) // 400)
    chart = [{"date": hist.index[i].strftime("%Y-%m-%d"), "close": round(closes[i], 2), "volume": volumes[i]}
             for i in range(0, len(closes), step)]

    low52 = info.get("fiftyTwoWeekLow") or min(closes)
    high52 = info.get("fiftyTwoWeekHigh") or max(closes)

    return {
        "symbol": symbol,
        "name": info.get("shortName") or info.get("longName") or symbol,
        "logo_url": logo_url,
        "currency": info.get("currency", "USD"),
        "quote": {"price": round(last, 2), "previous_close": round(prev, 2),
                  "change": round(change, 2), "change_percent": round(pct, 2)},
        "profile": {"sector": info.get("sector"), "industry": info.get("industry"),
                    "website": website,
                    "summary": (info.get("longBusinessSummary") or "")[:600],
                    "employees": info.get("fullTimeEmployees"), "country": info.get("country")},
        "valuation": {"market_cap": info.get("marketCap"), "enterprise_value": info.get("enterpriseValue"),
                      "trailing_pe": info.get("trailingPE"), "forward_pe": info.get("forwardPE"),
                      "price_to_book": info.get("priceToBook"), "dividend_yield": info.get("dividendYield"),
                      "beta": info.get("beta"), "profit_margin": info.get("profitMargins"),
                      "revenue_growth": info.get("revenueGrowth"), "earnings_growth": info.get("earningsGrowth")},
        "range_52w": {"low": round(low52, 2) if low52 else None, "high": round(high52, 2) if high52 else None,
                      "position_pct": round((last - low52) / (high52 - low52) * 100, 1)
                      if (low52 and high52 and high52 > low52) else None},
        "analyst": {"target_mean": info.get("targetMeanPrice"), "recommendation_key": info.get("recommendationKey"),
                    "recommendation_mean": info.get("recommendationMean"), "num_analysts": info.get("numberOfAnalystOpinions")},
        "indicators": ind,
        "signal": sig,
        "chart": chart,
    }
