import sys, os, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.store as store
import app.market as market
import app.trending as trending
import app.main as main

_tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
_tmp.close()
store.DATA_FILE = __import__("pathlib").Path(_tmp.name)
store.DATA_DIR = store.DATA_FILE.parent

_PRICES = {"AAPL": 190.0, "BTC-USD": 60000.0, "IBM": 200.0, "NVDA": 900.0, "TSLA": 250.0,
           "SPY": 470.0, "QQQ": 480.0, "ETH-USD": 3000.0, "TLT": 92.0, "GLD": 350.0}

def _fake_quote(symbol):
    s = symbol.strip().upper()
    if s not in _PRICES:
        raise ValueError(f"No data for symbol {s!r}")
    p = _PRICES[s]
    return {"symbol": s, "price": p, "previous_close": p, "change": 1.0,
            "change_percent": 0.5, "as_of": "2026-07-14"}

def _fake_quotes(symbols):
    return [_fake_quote(s) for s in symbols]

def _fake_trending(limit=25, region="US"):
    return [{"symbol": s, "short_name": None, "rank": None} for s in ["AAPL","IBM","BTC-USD","NVDA","TSLA"][:limit]]

def _fake_history(symbol, period="1y"):
    return [
        {"date": "2026-07-13", "close": 188.0, "volume": 40000000},
        {"date": "2026-07-14", "close": 190.0, "volume": 42000000},
    ]

def _fake_stock_report(symbol, period="1y"):
    s = symbol.strip().upper()
    return {
        "symbol": s, "name": s, "currency": "USD", "logo_url": None,
        "quote": {"symbol": s, "price": _PRICES.get(s, 100.0), "change": 1.0,
                  "change_percent": 0.5, "previous_close": _PRICES.get(s, 100.0) - 1.0},
        "chart": [{"date": "2026-07-13", "close": 188.0}, {"date": "2026-07-14", "close": 190.0}],
        "indicators": {"sma50": 185.0, "sma200": 170.0, "rsi": 55.0},
        "valuation": {"market_cap": 3e12, "trailing_pe": 30.0, "forward_pe": 28.0,
                      "price_to_book": 40.0, "dividend_yield": 0.005, "beta": 1.2,
                      "profit_margin": 0.25, "revenue_growth": 0.1, "earnings_growth": 0.12},
        "profile": {"sector": "Tech", "industry": "Consumer", "country": "US",
                    "employees": 1000, "website": "https://example.com", "summary": "Co."},
        "analyst": {"target_mean": 210.0, "recommendation_key": "buy",
                    "recommendation_mean": 2.0, "num_analysts": 30},
        "range_52w": {"low": 150.0, "high": 200.0, "position_pct": 80.0},
        "signal": {"action": "BUY", "score": 4, "confidence": "high",
                   "reasons": ["uptrend", "healthy momentum"]},
    }

def _fake_candidates(region="US", extra=None):
    # Deterministic, offline universe for ranking tests.
    return ["AAPL", "NVDA", "TSLA", "SPY", "GLD", "BTC-USD"]

market.get_quote = _fake_quote
market.get_quotes = _fake_quotes
market.get_trending = _fake_trending
market.get_history = _fake_history
market.get_stock_report = _fake_stock_report
trending.get_candidates = _fake_candidates
main.get_quote = _fake_quote
main.get_quotes = _fake_quotes
main.get_trending = _fake_trending
main.get_history = _fake_history
main.get_stock_report = _fake_stock_report
store.get_quote = _fake_quote
