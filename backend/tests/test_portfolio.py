"""Pure unit tests for portfolio math (no network)."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

from portfolio import portfolio_value, asset_allocation


def test_empty_portfolio():
    r = portfolio_value([], {})
    assert r["market_value"] == 0
    assert r["total_gain"] == 0


def test_portfolio_value_and_gain():
    positions = [
        {"symbol": "AAPL", "quantity": 10, "cost_basis": 150},
        {"symbol": "SPY", "quantity": 5, "cost_basis": 400},
    ]
    prices = {"AAPL": 190, "SPY": 470}
    r = portfolio_value(positions, prices)
    assert r["market_value"] == 10*190 + 5*470
    assert r["cost_basis_total"] == 10*150 + 5*400
    assert r["total_gain"] == 750
    assert abs(r["total_gain_pct"] - round(750/3500*100, 2)) < 1e-6


def test_position_level_gain():
    r = portfolio_value([{"symbol": "AAPL", "quantity": 10, "cost_basis": 150}], {"AAPL": 190})
    p = r["positions"][0]
    assert p["market_value"] == 1900
    assert p["gain"] == 400


def test_allocation_weights_sum_100():
    positions = [
        {"symbol": "AAPL", "quantity": 10, "cost_basis": 150, "category": "Stocks"},
        {"symbol": "BTC-USD", "quantity": 1, "cost_basis": 40000, "category": "Crypto"},
    ]
    prices = {"AAPL": 200, "BTC-USD": 80000}
    alloc = asset_allocation(positions, prices)
    total_w = sum(a["weight"] for a in alloc)
    assert abs(total_w - 100) < 1e-6
    assert alloc[0]["category"] == "Crypto"
