# Investor — Changelog

Local investment research web app. Runs on this laptop (network-reachable, not
just localhost) with a transparent, long-horizon "skyrocket" ranking.

## Features
- **Top 25 Skyrocket list** (homepage): 0–100 transparent score across a broad
  liquid universe (mega-cap stocks, ETFs, commodities, bonds, crypto).
- **Model Track Record** card: realized 1y return, max drawdown, and signal
  agreement % across the ranked universe (`/api/backtest`).
- **Stock Research**: chart, valuation, analyst targets, rule-based BUY/HOLD/SELL.
- **Trending**, **Copy Trading** (follow public investors + log ideas),
  **Price Alerts** (with check engine), **Portfolio** analytics.
- **Offline resilience**: curated fallback reports + TTL cache; UI flags
  offline snapshots honestly.
- **One-command launch**: `./run.sh`, `./start-service.sh`, `./install-service.sh`
  (launchd + systemd auto-start), `Makefile`, Dockerfile, GitHub Actions CI.

## Transparency
The Skyrocket score is fully explainable (trend, RSI, analyst upside, growth,
margin of safety, rule-based signal). See the "How the Skyrocket score works"
panel in the app. Long-horizon view — not day-trading.

## Tests
Full offline suite (`pytest`, configured via `pytest.ini`). All market calls are
stubbed in `tests/conftest.py`, so the suite runs without network access.
