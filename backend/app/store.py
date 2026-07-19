"""Local JSON persistence for user data: alerts, followed traders, watchlist.

No external database required. Everything lives in data/appdata.json.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "appdata.json"
_lock = threading.Lock()

DEFAULT_DATA = {
    "alerts": [],          # {id, symbol, condition: 'above'|'below', price, active, fired, created}
    "followed_traders": [], # [trader_id]
    "traders_ideas": {},   # trader_id -> [ {symbol, action, target, note, date} ]
    "watchlist": [],       # [symbol]
}


def _ensure():
    DATA_DIR.mkdir(exist_ok=True)
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text())
            if isinstance(data, dict) and data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass
    DATA_FILE.write_text(json.dumps(DEFAULT_DATA, indent=2))
    return json.loads(DATA_FILE.read_text())


def _save(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


def load() -> dict:
    with _lock:
        return _ensure()


def save(data: dict):
    with _lock:
        _save(data)


# ---- Alerts ----
def get_alerts() -> list:
    return load().get("alerts", [])


def add_alert(symbol: str, condition: str, price: float) -> dict:
    data = load()
    alert = {
        "id": len(data["alerts"]) + 1,
        "symbol": symbol.strip().upper(),
        "condition": condition,
        "price": float(price),
        "active": True,
        "fired": False,
        "created": _now(),
    }
    data["alerts"].append(alert)
    save(data)
    return alert


def remove_alert(alert_id: int) -> bool:
    data = load()
    before = len(data["alerts"])
    data["alerts"] = [a for a in data["alerts"] if a["id"] != alert_id]
    save(data)
    return len(data["alerts"]) < before


def _now():
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")


# ---- Followed traders ----
def get_followed() -> list:
    return load().get("followed_traders", [])


def follow(trader_id: str) -> list:
    data = load()
    if trader_id not in data["followed_traders"]:
        data["followed_traders"].append(trader_id)
        save(data)
    return data["followed_traders"]


def unfollow(trader_id: str) -> list:
    data = load()
    data["followed_traders"] = [t for t in data["followed_traders"] if t != trader_id]
    save(data)
    return data["followed_traders"]


def add_idea(trader_id: str, symbol: str, action: str, target: float | None, note: str) -> dict:
    data = load()
    ideas = data.setdefault("traders_ideas", {}).setdefault(trader_id, [])
    idea = {
        "symbol": symbol.strip().upper(),
        "action": action,
        "target": (float(target) if target not in (None, "") else None),
        "note": note,
        "date": _now(),
    }
    ideas.append(idea)
    save(data)
    return idea


def get_ideas(trader_id: str) -> list:
    return load().get("traders_ideas", {}).get(trader_id, [])
