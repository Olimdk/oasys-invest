import yfinance as yf

t = yf.Ticker("AAPL")
h = t.history(period="5d")
print("ROWS", len(h))
if len(h):
    print(h[["Close"]].tail(3).to_string())
else:
    print("NO DATA — likely offline or rate-limited")

# also try a few asset classes
for sym in ["SPY", "BTC-USD", "TLT", "GLD"]:
    try:
        tt = yf.Ticker(sym)
        hh = tt.history(period="5d")
        print(sym, "last close:", round(hh["Close"].iloc[-1], 2) if len(hh) else "none")
    except Exception as e:
        print(sym, "error:", e)
