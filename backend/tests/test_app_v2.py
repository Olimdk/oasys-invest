"""Tests for trending, traders, alerts, follow (market stubbed via conftest)."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import app.main as main
client = TestClient(main.app)


def test_trending():
    r = client.get("/api/trending?limit=3")
    assert r.status_code == 200
    assert len(r.json()) == 3
    assert r.json()[0]["symbol"] == "AAPL"


def test_traders_list():
    r = client.get("/api/traders")
    assert r.status_code == 200
    assert any(t["id"] == "buffett" for t in r.json())


def test_follow_and_ideas():
    r = client.post("/api/follow/buffett")
    assert r.status_code == 200
    assert "buffett" in r.json()["followed"]
    r2 = client.post("/api/traders/buffett/ideas", json={"symbol": "AAPL", "action": "buy", "target": 320, "note": "x"})
    assert r2.status_code == 200
    assert r2.json()["symbol"] == "AAPL"


def test_alerts_crud():
    a = client.post("/api/alerts", json={"symbol": "AAPL", "condition": "above", "price": 999})
    assert a.status_code == 200
    aid = a.json()["id"]
    assert client.get("/api/alerts").status_code == 200
    c = client.post("/api/check-alerts")
    assert c.status_code == 200
    assert c.json()["count"] == 0
    assert client.delete(f"/api/alerts/{aid}").status_code == 200


def test_check_alert_fires():
    a = client.post("/api/alerts", json={"symbol": "IBM", "condition": "below", "price": 250})
    assert a.status_code == 200
    c = client.post("/api/check-alerts")
    assert c.json()["count"] == 1
