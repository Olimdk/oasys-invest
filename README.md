# OASYS Invest

A local-first investment research desktop app. Live market data (stocks, ETFs,
crypto, bonds, commodities), a transparent buy/hold/sell signal, community-trending
tickers, a copy-trading tracker for well-known public investors, price alerts, and a
portfolio analyzer — all wrapped in a native desktop window (Tauri) with a Python
(FastAPI) engine underneath.

The desktop app shows the **exact same UI as the web app**: the Tauri window loads the
engine's own front end (served from the bundled backend on `127.0.0.1:8000`), so the
design, content, and behaviour are identical whether you run it in a browser or as a
native window.

Built to run fully on your machine. No account, no telemetry. When the network is
unavailable it degrades gracefully to a curated offline snapshot so the app stays
useful on a laptop with limited connectivity.

## Features
- **Stock research** — price chart, valuation, analyst targets, 52-week range, and a
  rule-based BUY/HOLD/SELL signal (RSI + moving averages + valuation).
- **Trending** — top community-interest tickers (Yahoo Finance trending).
- **Skyrocket radar** — ranked long-horizon candidates across mega-cap stocks, ETFs,
  commodities, bonds, and major crypto.
- **Copy-trading tracker** — follow public investors and log their ideas.
- **Alerts** — price triggers with a `check-alerts` engine.
- **Portfolio** — market value, gain, and asset allocation by category.

## Install (one command)

    curl -fsSL https://raw.githubusercontent.com/Olimdk/oasys-invest/main/install.sh | bash

The installer clones OASYS Invest, creates a Python virtualenv for the engine, builds the
native desktop shell, and drops an `oasys-invest` launcher on your PATH.

## Install (from a clone)

    git clone https://github.com/Olimdk/oasys-invest.git
    cd oasys-invest
    ./install.sh

## Run

    oasys-invest

Or during development:

    cd src-tauri && cargo run --release

## Architecture

- `backend/` — the FastAPI investment engine (`app.main`). It also serves the desktop
  UI from `backend/app/static/` at `http://127.0.0.1:8000`.
- `src-tauri/` — Rust/Tauri shell. At startup it spawns the bundled engine and opens a
  native window pointed directly at `http://127.0.0.1:8000`, so the desktop app is the
  web app — same content, same design.
- `backend/.venv/` — Python virtualenv (gitignored; created by `install.sh`).

When the network is unavailable, the engine serves a curated offline snapshot so the
app remains usable.

## License

MIT © 2026 Oliver
