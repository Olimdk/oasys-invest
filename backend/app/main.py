"""Investor — investment app: live data, analytics, trending, copy-trading, alerts."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .market import get_quote, get_history, get_quotes, get_stock_report
from .portfolio import portfolio_value, asset_allocation
from .trending import get_trending, get_candidates
from .traders import all_traders, get_trader
from .store import (
    get_alerts, add_alert, remove_alert,
    get_followed, follow, unfollow, add_idea, get_ideas,
)
from .ranking import skyrocket_score, performance_stats
from .daytrade import daytrade_score
from .wisdom import wisdom_for
from .projection import project
from .vision_trade import analyze_trade_image
from . import fallback

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Investor", version="0.6.0",
              description="Live markets, trending tickers, copy-trading tracker, and price alerts.")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class QuoteRequest(BaseModel):
    symbol: str


class QuotesRequest(BaseModel):
    symbols: list[str]


class HistoryRequest(BaseModel):
    symbol: str
    period: str = "1mo"


class Position(BaseModel):
    symbol: str
    quantity: float = Field(..., gt=0)
    cost_basis: float = Field(..., ge=0)
    category: str = "Other"


class PortfolioRequest(BaseModel):
    positions: list[Position]
    prices: dict[str, float]


class AlertRequest(BaseModel):
    symbol: str
    condition: str = Field(..., pattern="^(above|below)$")
    price: float = Field(..., gt=0)


class IdeaRequest(BaseModel):
    symbol: str
    action: str = Field(..., pattern="^(buy|sell)$")
    target: float | None = None
    note: str = ""


class TradeImageRequest(BaseModel):
    image: str  # base64 (with or without data: prefix)


@app.get("/api/info")
def info():
    return {"name": "Investor", "version": "0.6.0",
            "endpoints": ["/api/trending", "/api/top-picks", "/api/decision/{symbol}",
                          "/api/analyze-trade-image", "/api/backtest", "/api/spark/{symbol}",
                          "/api/stock/{symbol}", "/api/alerts", "/api/traders",
                          "/api/follow", "/api/check-alerts"]}


@app.post("/api/quote")
def api_quote(req: QuoteRequest):
    try:
        return get_quote(req.symbol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/quotes")
def api_quotes(req: QuotesRequest):
    try:
        return get_quotes(req.symbols)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/history")
def api_history(req: HistoryRequest):
    try:
        return get_history(req.symbol, req.period)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/stock/{symbol}")
def api_stock(symbol: str, period: str = "1y"):
    try:
        return get_stock_report(symbol, period)
    except ValueError:
        rep = fallback.get_fallback_report(symbol)
        if rep:
            return {**rep, "offline": True}
        raise HTTPException(status_code=404, detail=f"No data for symbol {symbol!r}")


@app.get("/api/trending")
def api_trending(limit: int = Query(25, le=50), region: str = "US"):
    return get_trending(limit=limit, region=region)


@app.get("/api/spark/{symbol}")
def api_spark(symbol: str, period: str = "1y"):
    try:
        report = get_stock_report(symbol, period)
    except ValueError:
        report = fallback.get_fallback_report(symbol)
        if report is None:
            raise HTTPException(status_code=404, detail=f"No data for symbol {symbol!r}")
        report = {**report, "offline": True}
    chart = report.get("chart", [])
    closes = [c["close"] for c in chart if c.get("close") is not None]
    if not closes:
        return {"symbol": symbol, "closes": [], "return_1y_pct": None, "offline": report.get("offline", False)}
    step = max(1, len(closes) // 60)
    sampled = closes[::step]
    if sampled[-1] != closes[-1]:
        sampled.append(closes[-1])
    ret = (closes[-1] - closes[0]) / closes[0] * 100 if closes[0] else 0.0
    return {"symbol": symbol, "closes": [round(x, 2) for x in sampled],
            "return_1y_pct": round(ret, 2), "offline": report.get("offline", False)}


def _score_pick(sym, mode):
    try:
        report = get_stock_report(sym, "1y")
        offline = False
    except ValueError:
        report = fallback.get_fallback_report(sym)
        if report is None:
            return None
        report = {**report, "offline": True}
        offline = True
    sc = daytrade_score(report) if mode == "daytrade" else skyrocket_score(report)
    return {
        "symbol": sym,
        "name": report.get("name"),
        "price": report.get("quote", {}).get("price"),
        "change_percent": report.get("quote", {}).get("change_percent"),
        "score": sc["score"],
        "grade": sc["grade"],
        "action": sc["action"],
        "reasons": sc["reasons"],
        "offline": offline,
        "wisdom": [w["name"] for w in wisdom_for(report) if w["match"]],
        "projection": project(report, horizon_bars=21, mode=mode),
    }


@app.get("/api/top-picks")
def api_top_picks(limit: int = Query(25, le=50), region: str = "US",
                  include_curated: bool = Query(True),
                  mode: str = Query("long", pattern="^(long|daytrade)$")):
    symbols = get_candidates(region=region, include_curated=include_curated)
    picks = []
    for sym in symbols:
        p = _score_pick(sym, mode)
        if p:
            picks.append(p)
    picks.sort(key=lambda p: p["score"], reverse=True)
    return picks[:limit]


@app.get("/api/decision/{symbol}")
def api_decision(symbol: str, mode: str = Query("long", pattern="^(long|daytrade)$")):
    symbol = symbol.strip().upper()
    try:
        report = get_stock_report(symbol, "1y")
        offline = False
    except ValueError:
        report = fallback.get_fallback_report(symbol)
        if report is None:
            raise HTTPException(status_code=404, detail=f"No data for symbol {symbol!r}")
        report = {**report, "offline": True}
        offline = True
    long_sc = skyrocket_score(report)
    day_sc = daytrade_score(report)
    wisdom = wisdom_for(report)
    proj_long = project(report, horizon_bars=21, mode="long")
    proj_day = project(report, horizon_bars=5, mode="daytrade")
    copytrade = []
    for t in all_traders():
        for idea in get_ideas(t["id"]):
            if idea.get("symbol") == symbol:
                copytrade.append({"investor": t["name"], **idea})
    return {
        "symbol": symbol, "offline": offline,
        "name": report.get("name"),
        "price": report.get("quote", {}).get("price"),
        "engine": {
            "long": {k: long_sc[k] for k in ("score", "grade", "action", "reasons")},
            "daytrade": {k: day_sc[k] for k in ("score", "grade", "action", "reasons")},
        },
        "projection": {"long": proj_long, "daytrade": proj_day},
        "wisdom": wisdom,
        "copytrade_ideas": copytrade,
        "report": report,
    }


@app.post("/api/analyze-trade-image")
def api_analyze_trade_image(req: TradeImageRequest):
    """Paste/insert a screenshot of a trade or chart; get BUY/SELL/HOLD.

    The image is analyzed fully on-device (OCR + color/trend heuristics). If a
    ticker is detected, the live engine score is blended in. Nothing leaves
    the machine.
    """
    def live_engine(sym):
        try:
            report = get_stock_report(sym, "1y")
            sc = daytrade_score(report)
            return {"score": sc["score"], "action": sc["action"], "grade": sc["grade"]}
        except ValueError:
            return None
    return analyze_trade_image(req.image, live_engine=live_engine)


@app.get("/api/backtest")
def api_backtest(region: str = "US", include_curated: bool = Query(True),
                 mode: str = Query("long", pattern="^(long|daytrade)$")):
    symbols = get_candidates(region=region, include_curated=include_curated)
    rows = []
    agree = 0
    total = 0
    for sym in symbols:
        try:
            report = get_stock_report(sym, "1y")
        except ValueError:
            report = fallback.get_fallback_report(sym)
            if report is None:
                continue
            report = {**report, "offline": True}
        stats = performance_stats(report.get("chart", []))
        if stats.get("return_1y_pct") is None:
            continue
        action = (report.get("signal") or {}).get("action", "HOLD")
        positive = stats["return_1y_pct"] >= 0
        agreed = (action in ("BUY", "HOLD") and positive) or (action == "SELL" and not positive)
        total += 1
        if agreed:
            agree += 1
        rows.append({"symbol": sym, "action": action, **stats, "offline": report.get("offline", False)})
    hit_rate = round(agree / total * 100, 1) if total else None
    return {"universe_size": total, "signal_agreement_pct": hit_rate,
            "avg_return_1y_pct": round(sum(r["return_1y_pct"] for r in rows) / total, 2) if total else None,
            "detail": rows}


@app.post("/api/movers")
def api_movers():
    watch = ["AAPL", "NVDA", "TSLA", "SPY", "QQQ", "BTC-USD", "ETH-USD", "TLT", "GLD"]
    out = []
    for sym in watch:
        try:
            out.append(get_quote(sym))
        except ValueError:
            continue
    out.sort(key=lambda q: abs(q["change_percent"]), reverse=True)
    return out


@app.get("/api/traders")
def api_traders():
    followed = set(get_followed())
    return [{"followed": t["id"] in followed, **t} for t in all_traders()]


@app.get("/api/traders/{trader_id}")
def api_trader(trader_id: str):
    t = get_trader(trader_id)
    if not t:
        raise HTTPException(status_code=404, detail="trader not found")
    return {"profile": t, "ideas": get_ideas(trader_id), "followed": trader_id in get_followed()}


@app.post("/api/follow/{trader_id}")
def api_follow(trader_id: str):
    if not get_trader(trader_id):
        raise HTTPException(status_code=404, detail="trader not found")
    return {"followed": follow(trader_id)}


@app.delete("/api/follow/{trader_id}")
def api_unfollow(trader_id: str):
    return {"followed": unfollow(trader_id)}


@app.post("/api/traders/{trader_id}/ideas")
def api_add_idea(trader_id: str, req: IdeaRequest):
    if not get_trader(trader_id):
        raise HTTPException(status_code=404, detail="trader not found")
    return add_idea(trader_id, req.symbol, req.action, req.target, req.note)


@app.get("/api/alerts")
def api_get_alerts():
    return get_alerts()


@app.post("/api/alerts")
def api_add_alert(req: AlertRequest):
    return add_alert(req.symbol, req.condition, req.price)


@app.delete("/api/alerts/{alert_id}")
def api_remove_alert(alert_id: int):
    if not remove_alert(alert_id):
        raise HTTPException(status_code=404, detail="alert not found")
    return {"ok": True}


@app.post("/api/check-alerts")
def api_check_alerts():
    alerts = get_alerts()
    fired = []
    changed = False
    for a in alerts:
        if not a.get("active") or a.get("fired"):
            continue
        try:
            price = get_quote(a["symbol"])["price"]
        except Exception:
            continue
        hit = (a["condition"] == "above" and price >= a["price"]) or \
              (a["condition"] == "below" and price <= a["price"])
        if hit:
            a["fired"] = True
            a["active"] = False
            a["triggered_price"] = price
            fired.append({"symbol": a["symbol"], "price": price,
                          "condition": a["condition"], "target": a["price"]})
            changed = True
    if changed:
        from .store import save, load
        save(load())
    return {"fired": fired, "count": len(fired)}


@app.post("/api/portfolio")
def api_portfolio(req: PortfolioRequest):
    prices = {k.upper(): v for k, v in req.prices.items()}
    return portfolio_value([p.model_dump() for p in req.positions], prices)


@app.post("/api/allocation")
def api_allocation(req: PortfolioRequest):
    prices = {k.upper(): v for k, v in req.prices.items()}
    return asset_allocation([p.model_dump() for p in req.positions], prices)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import argparse
    import uvicorn
    parser = argparse.ArgumentParser(description="Investor web app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port, reload=False)
