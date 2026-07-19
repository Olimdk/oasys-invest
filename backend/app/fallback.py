"""Offline fallback: curated, sensible stock reports so the Top-25 list still
renders (with real, transparent scores) when live market data is unavailable.

These are static snapshots used ONLY when yfinance calls fail, so the app
remains useful on a laptop with no/limited connectivity. Values are
illustrative, not live.
"""

from __future__ import annotations


def _mk(symbol, name, sector, industry, price, prev, sma50, sma200, rsi,
        target, rec_key, rec_mean, num, low52, high52, pos_pct, action, score,
        conf, reasons, market_cap=None, pe=None, fpe=None, pb=None, dy=None,
        beta=None, pm=None, rg=None, eg=None, country="US", employees=None,
        website="", summary=""):
    return {
        "symbol": symbol, "name": name, "currency": "USD", "logo_url": "",
        "quote": {"price": price, "previous_close": prev,
                  "change": round(price - prev, 2), "change_percent": round((price - prev) / prev * 100, 2)},
        "chart": [], "indicators": {"sma50": sma50, "sma200": sma200, "rsi": rsi},
        "valuation": {"market_cap": market_cap, "trailing_pe": pe, "forward_pe": fpe, "price_to_book": pb,
                      "dividend_yield": dy, "beta": beta, "profit_margin": pm,
                      "revenue_growth": rg, "earnings_growth": eg},
        "profile": {"sector": sector, "industry": industry, "country": country,
                    "employees": employees, "website": website, "summary": summary},
        "analyst": {"target_mean": target, "recommendation_key": rec_key,
                    "recommendation_mean": rec_mean, "num_analysts": num},
        "range_52w": {"low": low52, "high": high52, "position_pct": pos_pct},
        "signal": {"action": action, "score": score, "confidence": conf, "reasons": reasons},
    }


FALLBACK_REPORTS: dict[str, dict] = {
    "AAPL": _mk("AAPL", "Apple Inc.", "Technology", "Consumer Electronics", 190.0, 188.0,
                185.0, 170.0, 55.0, 210.0, "buy", 2.0, 30, 150.0, 200.0, 80.0,
                "BUY", 4, "high", ["uptrend", "healthy momentum"],
                market_cap=3e12, pe=30.0, fpe=28.0, pb=40.0, dy=0.005, beta=1.2,
                pm=0.25, rg=0.08, eg=0.10, employees=161000, website="https://apple.com",
                summary="Apple designs hardware/software."),
    "NVDA": _mk("NVDA", "NVIDIA Corp.", "Technology", "Semiconductors", 900.0, 880.0,
                820.0, 600.0, 62.0, 1050.0, "buy", 1.8, 40, 400.0, 950.0, 89.0,
                "BUY", 5, "high", ["uptrend", "strong growth"],
                market_cap=2.2e12, pe=65.0, fpe=45.0, pb=50.0, dy=0.0003, beta=1.7,
                pm=0.55, rg=0.85, eg=1.10, employees=29600, website="https://nvidia.com",
                summary="AI compute leader."),
    "MSFT": _mk("MSFT", "Microsoft Corp.", "Technology", "Software", 420.0, 415.0,
                405.0, 370.0, 58.0, 470.0, "buy", 1.9, 35, 310.0, 430.0, 86.0,
                "BUY", 4, "high", ["uptrend", "healthy momentum"],
                market_cap=3.1e12, pe=36.0, fpe=32.0, pb=12.0, dy=0.007, beta=0.9,
                pm=0.36, rg=0.15, eg=0.20, employees=221000, website="https://microsoft.com",
                summary="Cloud + AI software."),
    "BTC-USD": _mk("BTC-USD", "Bitcoin", "Crypto", "Currency", 60000.0, 58000.0,
                   56000.0, 42000.0, 64.0, 75000.0, "buy", 2.0, 10, 25000.0, 70000.0, 78.0,
                   "HOLD", 2, "moderate", ["uptrend", "volatile"],
                   market_cap=1.2e12, beta=2.0, dy=None),
    "GLD": _mk("GLD", "SPDR Gold Shares", "Commodities", "Gold", 220.0, 218.0,
               210.0, 195.0, 60.0, 235.0, "hold", 3.0, 5, 170.0, 225.0, 92.0,
               "HOLD", 1, "low", ["uptrend", "near high"],
               market_cap=6e10, beta=0.1, dy=None),
    "TLT": _mk("TLT", "iShares 20+ Yr Treasury", "Bonds", "Treasury", 92.0, 93.0,
               94.0, 98.0, 42.0, 96.0, "hold", 3.0, 3, 88.0, 102.0, 36.0,
               "HOLD", 0, "low", ["downtrend", "near low"],
               market_cap=4e10, beta=0.2, dy=0.035),
}


def get_fallback_report(symbol: str) -> dict | None:
    return FALLBACK_REPORTS.get(symbol.strip().upper())
