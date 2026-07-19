"""Tests for the skyrocket ranking + /api/top-picks endpoint (offline)."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import app.main as main
import app.market as market
import app.trending as trending
client = TestClient(main.app)


def test_top_picks_returns_scored_list():
    r = client.get("/api/top-picks?limit=3")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 3
    for p in data:
        assert "score" in p and 0 <= p["score"] <= 100
        assert "grade" in p
        assert isinstance(p["reasons"], list) and p["reasons"]


def test_top_picks_sorted_desc():
    r = client.get("/api/top-picks?limit=5")
    scores = [p["score"] for p in r.json()]
    assert scores == sorted(scores, reverse=True)


def test_top_picks_covers_broad_universe():
    r = client.get("/api/top-picks?limit=10")
    assert r.status_code == 200
    assert len(r.json()) >= 6


def test_top_picks_region_and_curated_params():
    r = client.get("/api/top-picks?limit=10&region=GB&include_curated=false")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    b = client.get("/api/backtest?region=DE&include_curated=false")
    assert b.status_code == 200
    assert "universe_size" in b.json()


def test_spark_endpoint_returns_closes():
    r = client.get("/api/spark/AAPL")
    assert r.status_code == 200
    d = r.json()
    assert d["symbol"] == "AAPL"
    assert isinstance(d["closes"], list)
    assert "return_1y_pct" in d


def test_top_picks_falls_back_offline():
    # Force live reports to fail -> curated fallback must still score & return.
    # Patch main's own reference to get_stock_report (imported into its namespace).
    real = main.get_stock_report
    main.get_stock_report = lambda s, p="1y": (_ for _ in ()).throw(ValueError("offline"))
    try:
        r = client.get("/api/top-picks?limit=10")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert any(p.get("offline") for p in data)
        for p in data:
            assert 0 <= p["score"] <= 100
    finally:
        main.get_stock_report = real


def test_backtest_returns_track_record():
    r = client.get("/api/backtest")
    assert r.status_code == 200
    d = r.json()
    assert "universe_size" in d and d["universe_size"] >= 1
    assert "signal_agreement_pct" in d
    assert "detail" in d and len(d["detail"]) >= 1
    for row in d["detail"]:
        assert "return_1y_pct" in row
        assert "max_drawdown_pct" in row


def test_info_lists_top_picks():
    r = client.get("/api/info")
    assert "/api/top-picks" in r.json()["endpoints"]
    assert "/api/backtest" in r.json()["endpoints"]
    assert "/api/spark/{symbol}" in r.json()["endpoints"]
