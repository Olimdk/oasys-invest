"""
Portfolio math for the Investor app.

Pure functions (no network) so they are trivially testable. A portfolio is a
list of positions: {"symbol", "quantity", "cost_basis", "category"}.
"""

from __future__ import annotations

from typing import Sequence


def portfolio_value(positions: Sequence[dict], prices: dict[str, float]) -> dict:
    if not positions:
        return {
            "market_value": 0.0,
            "cost_basis_total": 0.0,
            "total_gain": 0.0,
            "total_gain_pct": 0.0,
            "positions": [],
        }
    rows = []
    mv = 0.0
    cb = 0.0
    for p in positions:
        sym = p["symbol"].upper()
        qty = float(p["quantity"])
        basis = float(p["cost_basis"])
        price = float(prices.get(sym, 0.0))
        pos_mv = qty * price
        pos_cb = qty * basis
        gain = pos_mv - pos_cb
        gain_pct = (gain / pos_cb * 100) if pos_cb else 0.0
        mv += pos_mv
        cb += pos_cb
        rows.append({
            "symbol": sym,
            "quantity": qty,
            "avg_cost": round(basis, 2),
            "price": round(price, 2),
            "market_value": round(pos_mv, 2),
            "gain": round(gain, 2),
            "gain_percent": round(gain_pct, 2),
        })
    total_gain = mv - cb
    total_gain_pct = (total_gain / cb * 100) if cb else 0.0
    return {
        "market_value": round(mv, 2),
        "cost_basis_total": round(cb, 2),
        "total_gain": round(total_gain, 2),
        "total_gain_pct": round(total_gain_pct, 2),
        "positions": rows,
    }


def asset_allocation(positions: Sequence[dict], prices: dict[str, float]) -> list[dict]:
    values = {}
    for p in positions:
        sym = p["symbol"].upper()
        qty = float(p["quantity"])
        price = float(prices.get(sym, 0.0))
        cat = p.get("category", "Other")
        values[cat] = values.get(cat, 0.0) + qty * price
    total = sum(values.values()) or 1.0
    out = []
    for cat, val in sorted(values.items(), key=lambda kv: -kv[1]):
        out.append({"category": cat, "value": round(val, 2), "weight": round(val / total * 100, 2)})
    return out
