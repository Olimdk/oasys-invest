"""Community-trending tickers + a curated candidate universe for ranking."""

from __future__ import annotations

import urllib.request
import json


def get_trending(limit: int = 25, region: str = "US") -> list[dict]:
    """Return top community-interest tickers for a region.

    Falls back to a sensible default list if the network call fails.
    """
    url = f"https://query1.finance.yahoo.com/v1/finance/trending/{region}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = json.load(urllib.request.urlopen(req, timeout=15))
        quotes = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
        out = []
        for q in quotes[:limit]:
            sym = q.get("symbol")
            if not sym:
                continue
            out.append({
                "symbol": sym,
                "short_name": q.get("shortName"),
                "rank": q.get("rank"),
            })
        if out:
            return out
    except Exception:
        pass
    # Fallback default watchlist
    fallback = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META", "GOOGL", "SPY", "BTC-USD", "ETH-USD"]
    return [{"symbol": s, "short_name": None, "rank": None} for s in fallback[:limit]]


# Curated, liquid universe used to build the "Top 25 skyrocket" ranking.
# Spans mega-cap stocks, broad ETFs, commodities, bonds, and major crypto so the
# homepage reflects the best long-horizon candidates, not just today's trending.
CANDIDATE_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "JPM", "V",
    "UNH", "XOM", "JNJ", "WMT", "MA", "PG", "HD", "CVX", "KO", "PEP",
    "ABBV", "BAC", "PFE", "COST", "DIS", "CSCO", "TMO", "AVGO", "MCD", "NFLX",
    "AMD", "INTC", "QCOM", "IBM", "ORCL", "ADBE", "CRM", "TXN", "AMAT", "PYPL",
    "SPY", "QQQ", "VTI", "VOO", "IWM", "ARKK", "GLD", "SLV", "TLT", "HYG",
    "BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "ADA-USD", "LTC-USD",
]


def get_candidates(region: str = "US", include_curated: bool = True,
                   extra: list[str] | None = None) -> list[str]:
    """Trending tickers + (optionally) curated universe (deduped) for ranking."""
    syms: list[str] = []
    try:
        syms = [q.get("symbol") for q in get_trending(limit=25, region=region) if q.get("symbol")]
    except Exception:
        syms = []
    seen: set[str] = set()
    out: list[str] = []
    base = list(syms) + (list(CANDIDATE_UNIVERSE) if include_curated else []) + list(extra or [])
    for s in base:
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out
