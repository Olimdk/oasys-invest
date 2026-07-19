import yfinance as yf
import json

sym = "AAPL"
t = yf.Ticker(sym)
info = t.info
# Show the keys we care about
keys = ["shortName","longName","website","sector","industry","marketCap","enterpriseValue",
        "trailingPE","forwardPE","priceToBook","dividendYield","beta","profitMargins",
        "revenueGrowth","earningsGrowth","totalCash","totalDebt","currentRatio",
        "fiftyTwoWeekHigh","fiftyTwoWeekLow","fiftyDayAverage","twoHundredDayAverage",
        "regularMarketPrice","targetMeanPrice","recommendationMean","recommendationKey",
        "numberOfAnalystOpinions","currency"]
print("=== INFO (selected) ===")
for k in keys:
    print(k, "=", info.get(k))

print("\n=== NEWS (first 3) ===")
try:
    news = t.news
    for n in news[:3]:
        print("-", n.get("title"), "|", n.get("publisher"), "|", n.get("link"))
except Exception as e:
    print("news error:", e)

print("\n=== HISTORY 6mo ===")
h = t.history(period="6mo")
print("rows", len(h))
print(h[["Close","Volume"]].tail(2).to_string())
