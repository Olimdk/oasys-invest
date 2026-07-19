"""API tests (market stubbed at source via conftest)."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import app.main as main
client = TestClient(main.app)


def test_info_lists_new_endpoints():
    r = client.get("/api/info")
    assert r.status_code == 200
    ep = r.json()["endpoints"]
    assert "/api/trending" in ep
    assert "/api/stock/{symbol}" in ep


def test_quote_endpoint():
    r = client.post("/api/quote", json={"symbol": "AAPL"})
    assert r.status_code == 200
    assert r.json()["price"] == 190.0


def test_quote_not_found():
    r = client.post("/api/quote", json={"symbol": "ZZZNOPE"})
    assert r.status_code == 404


def test_history_endpoint():
    r = client.post("/api/history", json={"symbol": "AAPL", "period": "1mo"})
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_portfolio_endpoint():
    positions = [{"symbol": "AAPL", "quantity": 10, "cost_basis": 150, "category": "Stocks"}]
    prices = {"AAPL": 190}
    r = client.post("/api/portfolio", json={"positions": positions, "prices": prices})
    assert r.status_code == 200
    assert r.json()["market_value"] == 1900


def test_allocation_endpoint():
    positions = [
        {"symbol": "AAPL", "quantity": 10, "cost_basis": 150, "category": "Stocks"},
        {"symbol": "BTC-USD", "quantity": 1, "cost_basis": 40000, "category": "Crypto"},
    ]
    prices = {"AAPL": 200, "BTC-USD": 80000}
    r = client.post("/api/allocation", json={"positions": positions, "prices": prices})
    assert r.status_code == 200
    assert r.json()[0]["category"] == "Crypto"
