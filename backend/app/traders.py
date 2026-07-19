"""Curated, publicly-documented profitable investors/traders to follow.

These are real, widely-reported public figures and their *documented* styles.
We do NOT fabricate returns or live broker P&L. Each entry is a tracker profile
you can follow; you log their public ideas to build a copy-trading feed.
Sources are public (company filings, interviews, books) — summaries only.
"""

from __future__ import annotations

CURATED_TRADERS = [
    {
        "id": "buffett",
        "name": "Warren Buffett",
        "style": "Value / quality compounding",
        "known_for": "Berkshire Hathaway. Long-term, undervalued cash-generative businesses.",
        "theme": "Equity holdings concentrated in financials, consumer, energy, tech (Apple).",
        "source": "Public Berkshire Hathaway shareholder letters & 13F filings.",
    },
    {
        "id": "lynch",
        "name": "Peter Lynch",
        "style": "Growth-at-a-reasonable-price (GARP)",
        "known_for": "Fidelity Magellan. 'Invest in what you know.'",
        "theme": "Consumer brands, mid-cap growth, boring companies with steady earnings.",
        "source": "Public books/interviews (One Up on Wall Street).",
    },
    {
        "id": "dalio",
        "name": "Ray Dalio",
        "style": "Global macro / risk parity",
        "known_for": "Bridgewater. Diversified across asset classes, manages downside.",
        "theme": "Broad diversification, macro regimes, inflation/deflation hedges.",
        "source": "Public writings (Principles, Economic Machine).",
    },
    {
        "id": "cohen",
        "name": "Steve Cohen",
        "style": "Multi-strategy / fundamental + quant",
        "known_for": "Point72 / SAC. High-conviction, research-intensive.",
        "theme": "Technology, healthcare, consumer, with heavy fundamental research.",
        "source": "Public filings & reporting (13F).",
    },
    {
        "id": "burry",
        "name": "Michael Burry",
        "style": "Deep-value / contrarian",
        "known_for": "Scion. Asymmetric bets, concentrates when conviction is high.",
        "theme": "Contrarian value, occasionally thematic macro positions.",
        "source": "Public 13F filings & letters.",
    },
    {
        "id": "keynes",
        "name": "John Maynard Keynes",
        "style": "Concentrated value (early modern investing)",
        "known_for": "King's College endowment. 'Pick a few good stocks.'",
        "theme": "Concentrated, long-horizon quality businesses.",
        "source": "Historical public record (endowment reports).",
    },
]


def get_trader(trader_id: str):
    for t in CURATED_TRADERS:
        if t["id"] == trader_id:
            return t
    return None


def all_traders():
    return CURATED_TRADERS
