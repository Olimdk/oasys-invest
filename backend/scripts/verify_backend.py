import sys
sys.path.insert(0, "app")
from store import add_alert, get_alerts, follow, get_followed, add_idea, get_ideas
from traders import all_traders, get_trader
from trending import get_trending

print("store ok")
print("traders:", len(all_traders()))
print("trending5:", [t["symbol"] for t in get_trending(5)])

a = add_alert("AAPL", "above", 320)
print("alert id", a["id"], "active", a["active"])
print("alerts count", len(get_alerts()))
f = follow("buffett")
print("followed:", f)
i = add_idea("buffett", "AAPL", "buy", 320, "test idea")
print("idea added:", i["symbol"])
print("ideas:", get_ideas("buffett"))
