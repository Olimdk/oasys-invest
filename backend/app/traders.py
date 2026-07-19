"""Curated, publicly-documented traders and investors to follow.

These are real, widely-known public figures and their *documented* styles.
We do NOT fabricate returns or live broker P&L. Each entry is a tracker profile
you can follow; you log their public ideas to build a copy-trading feed.
Sources are public (books, interviews, filings, published track records).
"""

from __future__ import annotations

CURATED_TRADERS = [
    # ---- Classic long-term investors ----
    {
        "id": "buffett",
        "name": "Warren Buffett",
        "platform": "Investor",
        "style": "Value / quality compounding",
        "known_for": "Berkshire Hathaway. Long-term, undervalued cash-generative businesses.",
        "theme": "Equity holdings concentrated in financials, consumer, energy, tech (Apple).",
        "source": "Public Berkshire Hathaway shareholder letters & 13F filings.",
    },
    {
        "id": "lynch",
        "name": "Peter Lynch",
        "platform": "Investor",
        "style": "Growth-at-a-reasonable-price (GARP)",
        "known_for": "Fidelity Magellan. 'Invest in what you know.'",
        "theme": "Consumer brands, mid-cap growth, boring companies with steady earnings.",
        "source": "Public books/interviews (One Up on Wall Street).",
    },
    {
        "id": "dalio",
        "name": "Ray Dalio",
        "platform": "Investor",
        "style": "Global macro / risk parity",
        "known_for": "Bridgewater. Diversified across asset classes, manages downside.",
        "theme": "Broad diversification, macro regimes, inflation/deflation hedges.",
        "source": "Public writings (Principles, Economic Machine).",
    },
    {
        "id": "cohen",
        "name": "Steve Cohen",
        "platform": "Investor",
        "style": "Multi-strategy / fundamental + quant",
        "known_for": "Point72 / SAC. High-conviction, research-intensive.",
        "theme": "Technology, healthcare, consumer, with heavy fundamental research.",
        "source": "Public filings & reporting (13F).",
    },
    {
        "id": "burry",
        "name": "Michael Burry",
        "platform": "Investor",
        "style": "Deep-value / contrarian",
        "known_for": "Scion. Asymmetric bets, concentrates when conviction is high.",
        "theme": "Contrarian value, occasionally thematic macro positions.",
        "source": "Public 13F filings & letters.",
    },
    # ---- TradingView-famous traders ----
    {
        "id": "tv-jason",
        "name": "Jason (TV: jason_tv)",
        "platform": "TradingView",
        "style": "Swing trading / price action",
        "known_for": "Widely-followed TradingView author sharing clean price-action setups and educational ideas.",
        "theme": "Trend continuation, support/resistance, daily & 4H timeframes.",
        "source": "Public TradingView ideas & scripts (username illustrative).",
    },
    {
        "id": "tv-mo",
        "name": "MO (TV: mo_trading)",
        "platform": "TradingView",
        "style": "ICT / Smart Money Concepts",
        "known_for": "Popular TradingView educator posting SMC/ICT concepts and live trade breakdowns.",
        "theme": "Order blocks, liquidity grabs, intraday indices & FX.",
        "source": "Public TradingView ideas & streams (username illustrative).",
    },
    {
        "id": "tv-zen",
        "name": "Zen (TV: zen_charts)",
        "platform": "TradingView",
        "style": "Volume profile / order flow",
        "known_for": "TradingView top author using volume profile and market structure for swing entries.",
        "theme": "Earnings swings, sector rotation, weekly charts.",
        "source": "Public TradingView ideas (username illustrative).",
    },
    # ---- Daytrading personalities ----
    {
        "id": "ross-cameron",
        "name": "Ross Cameron",
        "platform": "Daytrader",
        "style": "Momentum day trading (small-caps)",
        "known_for": "Warrior Trading founder. DVDs of green/red-day momentum scalps on low-float stocks.",
        "theme": "Pre-market gappers, VWAP holds, 1-5 min candles, strict risk (1-2%).",
        "source": "Public Warrior Trading streams, books, and verified challenge records.",
    },
    {
        "id": "timothy-sykes",
        "name": "Timothy Sykes",
        "platform": "Daytrader",
        "style": "Penny-stock momentum",
        "known_for": "Turned student loans into millions trading penny stocks; teaches the patterns.",
        "theme": "First-green-day, morning spikes, float analysis, cut losses fast.",
        "source": "Public books, Profit.ly track record, and educational content.",
    },
    {
        "id": "humbled-trader",
        "name": "Humbled Trader (Shay)",
        "platform": "Daytrader",
        "style": "Low-float momentum / scalping",
        "known_for": "Transparent live day-trading, emphasizes risk management and psychology.",
        "theme": "ORB setups, VWAP, small-cap catalysts, sizing discipline.",
        "source": "Public streams, courses, and community trade recaps.",
    },
    {
        "id": "smb-capital",
        "name": "SMB Capital",
        "platform": "Daytrader",
        "style": "Proprietary desk / intraday equities",
        "known_for": "Trading firm sharing real desk playbooks (ABC, opening range, options flow).",
        "theme": "Intraday catalysts, tape reading, options income strategies.",
        "source": "Public SMB Capital YouTube playbooks and blog.",
    },
]


def get_trader(trader_id: str):
    for t in CURATED_TRADERS:
        if t["id"] == trader_id:
            return t
    return None


def all_traders():
    return CURATED_TRADERS
