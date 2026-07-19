"""Smoke test for the served frontend (offline)."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import app.main as main
client = TestClient(main.app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "Top 25" in r.text
    assert "Skyrocket" in r.text


def test_static_assets_served():
    for path in ["/static/styles.css", "/static/app.js"]:
        r = client.get(path)
        assert r.status_code == 200, path


def test_offline_indicator_present_in_assets():
    # The UI must be able to show an offline banner when live data fails.
    js = client.get("/static/app.js").text
    css = client.get("/static/styles.css").text
    assert "offline snapshot" in js
    assert "offline-banner" in css
    assert "offline-chip" in css


def test_settings_controls_and_persistence_present():
    html = client.get("/").text
    assert "set-region" in html
    assert "set-curated" in html
    js = client.get("/static/app.js").text
    assert "loadSettings" in js
    assert "saveSettings" in js
    assert "localStorage" in js


def test_track_record_present_in_assets():
    html = client.get("/").text
    assert "track-record" in html
    assert "Model Track Record" in html
    js = client.get("/static/app.js").text
    assert "loadTrackRecord" in js
    assert "/api/backtest" in js


def test_scoring_about_panel_present():
    html = client.get("/").text
    assert "How the Skyrocket score works" in html
    assert "about-card" in html
    assert "margin of safety" in html
