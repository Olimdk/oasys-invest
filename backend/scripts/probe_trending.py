import urllib.request, json

url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = json.load(urllib.request.urlopen(req, timeout=15))
    quotes = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
    print("TRENDING COUNT", len(quotes))
    for q in quotes[:15]:
        print(q.get("symbol"), "|", q.get("shortName"))
except Exception as e:
    print("ERR", repr(e))
