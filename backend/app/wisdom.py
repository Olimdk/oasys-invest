"""Investor wisdom overlay.

Encodes the *documented, public* investment criteria of well-known successful
investors (from the user's Obsidian "Financial Freedom / Trading" vault and
public filings/books) as transparent matchers. For a given stock report we
return which investors' styles currently align with the name, and why — so the
user sees "what the greats would likely favor" alongside the engine score.

This is NOT fabricated returns or live broker P&L. It is a style-match against
each investor's publicly stated philosophy. Clearly labeled as such.
"""

from __future__ import annotations

# Each matcher receives the stock report dict and returns (match: bool, reason: str).
# Criteria are derived from each investor's publicly documented approach.


def _buffett(r):
    """Quality compounding, durable earnings, reasonable valuation."""
    val = r.get("valuation") or {}
    ind = r.get("indicators") or {}
    pe = val.get("trailing_pe")
    eg = val.get("earnings_growth")
    reasons = []
    score = 0
    if eg is not None and eg > 0.10:
        score += 1; reasons.append("durable earnings growth (>10%)")
    if pe is not None and 0 < pe < 30:
        score += 1; reasons.append(f"reasonable trailing P/E ({pe:.0f})")
    if (val.get("profit_margin") or 0) > 0.15:
        score += 1; reasons.append("high profit margin (quality)")
    # prefers established, non-speculative
    if r.get("symbol", "").endswith("-USD"):
        score -= 2; reasons.append("avoids pure crypto/speculative")
    return score >= 2, "Buffett: " + (", ".join(reasons) if reasons else "no strong fit")


def _lynch(r):
    """Growth-at-a-reasonable-price; understandable consumer/niche leaders."""
    val = r.get("valuation") or {}
    eg = val.get("earnings_growth")
    peg = None
    if eg and val.get("trailing_pe"):
        peg = val["trailing_pe"] / (eg * 100)
    reasons = []
    score = 0
    if eg is not None and eg > 0.15:
        score += 1; reasons.append(f"strong earnings growth ({eg*100:.0f}%)")
    if peg is not None and peg < 1.5:
        score += 1; reasons.append(f"attractive PEG (~{peg:.1f})")
    return score >= 1, "Lynch: " + (", ".join(reasons) if reasons else "no strong fit")


def _dalio(r):
    """Global macro / diversification; favors low-correlation, inflation hedges."""
    sym = r.get("symbol", "")
    reasons = []
    score = 0
    # Hard assets / bonds / broad diversifiers
    if sym in ("GLD", "SLV", "TLT", "BTC-USD") or "ETF" in (r.get("name") or ""):
        score += 1; reasons.append("diversifying / low-correlation asset")
    if (r.get("valuation") or {}).get("beta") is not None and (r.get("valuation") or {}).get("beta") < 1:
        score += 1; reasons.append("lower beta (risk-parity friendly)")
    return score >= 1, "Dalio: " + (", ".join(reasons) if reasons else "no strong fit")


def _cohen(r):
    """Multi-strategy: high-conviction tech/healthcare with fundamental research."""
    profile = r.get("profile") or {}
    sector = (profile.get("sector") or "").lower()
    eg = (r.get("valuation") or {}).get("earnings_growth")
    reasons = []
    score = 0
    if sector in ("technology", "healthcare"):
        score += 1; reasons.append(f"core sector ({sector})")
    if eg is not None and eg > 0.15:
        score += 1; reasons.append("high growth")
    return score >= 1, "Cohen: " + (", ".join(reasons) if reasons else "no strong fit")


def _burry(r):
    """Deep-value / contrarian; asymmetric, out-of-favor names."""
    rng = r.get("range_52w") or {}
    pos = rng.get("position_pct")
    reasons = []
    score = 0
    if pos is not None and pos < 30:
        score += 1; reasons.append(f"near 52w low ({pos:.0f}% — value/contrarian)")
    if (r.get("valuation") or {}).get("trailing_pe") is not None and (r.get("valuation") or {}).get("trailing_pe") < 20:
        score += 1; reasons.append("low P/E (deep value)")
    return score >= 1, "Burry: " + (", ".join(reasons) if reasons else "no strong fit")


def _keynes(r):
    """Concentrated quality compounding."""
    eg = (r.get("valuation") or {}).get("earnings_growth")
    pm = (r.get("valuation") or {}).get("profit_margin")
    reasons = []
    score = 0
    if eg is not None and eg > 0.10:
        score += 1; reasons.append("compounding earnings")
    if pm is not None and pm > 0.15:
        score += 1; reasons.append("durable margin")
    return score >= 1, "Keynes: " + (", ".join(reasons) if reasons else "no strong fit")


MATCHERS = {
    "buffett": _buffett,
    "lynch": _lynch,
    "dalio": _dalio,
    "cohen": _cohen,
    "burry": _burry,
    "keynes": _keynes,
}


def wisdom_for(report: dict) -> list[dict]:
    """Return list of {investor, match, note} for all curated investors."""
    from .traders import all_traders
    out = []
    for t in all_traders():
        fn = MATCHERS.get(t["id"])
        if not fn:
            continue
        try:
            match, note = fn(report)
        except Exception:
            match, note = False, f"{t['name']}: no strong fit"
        out.append({"id": t["id"], "name": t["name"], "match": bool(match), "note": note})
    return out
