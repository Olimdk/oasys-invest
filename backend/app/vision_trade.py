"""On-device trade-image analyzer.

Given a pasted/saved screenshot of a trading chart or order ticket, this does
local (no-cloud) analysis:
  1. OCR any text (ticker, price, % change, BUY/SELL labels) via tesseract.
  2. Infer candle/line bias from pixel colors (green vs red dominance).
  3. Approximate the price trend slope from the chart's main line shape.
  4. If a ticker is detected, cross-reference the live engine score.
Returns a transparent BUY / SELL / HOLD recommendation with reasons.

All processing is local; nothing leaves the machine.
"""

from __future__ import annotations

import io
import re
import base64

try:
    from PIL import Image
    import pytesseract
    _HAVE_PIL = True
except Exception:
    _HAVE_PIL = False


def _decode_image(b64: str) -> "Image.Image | None":
    if not _HAVE_PIL:
        return None
    # strip data: prefix if present
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    try:
        raw = base64.b64decode(b64)
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        return None


def _ocr_text(img) -> str:
    try:
        return pytesseract.image_to_string(img) or ""
    except Exception:
        return ""


def _parse_ticker(text: str):
    # common tickers: 1-5 uppercase letters, possibly with -USD
    for m in re.finditer(r"\b([A-Z]{1,5}(?:-USD|-USD)?)\b", text):
        tok = m.group(1)
        if tok in ("BUY", "SELL", "HOLD", "USD", "API", "RSS", "CEO", "ROI"):
            continue
        return tok
    return None


def _parse_numbers(text: str):
    price = None
    pct = None
    for m in re.finditer(r"\$\s?([\d,]+\.?\d*)", text):
        try:
            price = float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    for m in re.finditer(r"([-+]?\d+\.?\d*)\s?%", text):
        try:
            pct = float(m.group(1))
        except ValueError:
            pass
    return price, pct


def _color_bias(img):
    """Return (green_ratio, red_ratio) of pixels that are clearly green/red."""
    small = img.resize((160, 120))
    px = list(small.getdata())
    g = r = tot = 0
    for (rr, gg, bb) in px:
        tot += 1
        if gg > rr + 25 and gg > bb + 10:
            g += 1
        elif rr > gg + 25 and rr > bb + 10:
            r += 1
    return (g / tot, r / tot) if tot else (0.0, 0.0)


def _trend_slope(img):
    """Approximate slope of the darkest/most-contrasting line by column centroid.

    Returns a value in roughly [-1, 1] where positive = up-trending chart.
    """
    gray = img.convert("L").resize((120, 90))
    w, h = gray.size
    px = gray.load()
    col_y = []
    for x in range(w):
        # brightest (line on white bg) row per column
        best_y, best_v = 0, -1
        for y in range(h):
            v = px[x, y]
            if v > best_v:
                best_v, best_y = v, y
        col_y.append(best_y)
    if len(col_y) < 2:
        return 0.0
    # slope: does the line go up (y decreases) left->right?
    dy = col_y[-1] - col_y[0]
    return -dy / h  # normalize


def analyze_trade_image(b64: str, live_engine=None) -> dict:
    """Analyze a base64 image. live_engine is optional callable(symbol)->dict."""
    if not _HAVE_PIL:
        return {"ok": False, "error": "image libraries unavailable", "action": "HOLD",
                "reasons": ["Pillow/pytesseract not installed."]}
    img = _decode_image(b64)
    if img is None:
        return {"ok": False, "error": "could not decode image", "action": "HOLD",
                "reasons": ["Image data was not valid."]}

    text = _ocr_text(img)
    ticker = _parse_ticker(text)
    price, pct = _parse_numbers(text)
    g_ratio, r_ratio = _color_bias(img)
    slope = _trend_slope(img)

    reasons = []
    score = 50  # neutral start

    # Text signals
    up_word = bool(re.search(r"\b(BUY|LONG|CALL)\b", text, re.I))
    down_word = bool(re.search(r"\b(SELL|SHORT|PUT)\b", text, re.I))
    if up_word and not down_word:
        score += 15; reasons.append("Order/text labeled BUY/LONG.")
    elif down_word and not up_word:
        score -= 15; reasons.append("Order/text labeled SELL/SHORT.")
    if pct is not None:
        if pct > 1:
            score += 6; reasons.append(f"Detected gain +{pct:.1f}% (momentum up).")
        elif pct < -1:
            score -= 6; reasons.append(f"Detected loss {pct:.1f}% (momentum down).")

    # Color bias (candles)
    if g_ratio > r_ratio + 0.04:
        score += 12; reasons.append(f"Chart is predominantly green (bullish candles {g_ratio*100:.0f}%).")
    elif r_ratio > g_ratio + 0.04:
        score -= 12; reasons.append(f"Chart is predominantly red (bearish candles {r_ratio*100:.0f}%).")

    # Trend slope
    if slope > 0.12:
        score += 12; reasons.append("Chart line trends upward.")
    elif slope < -0.12:
        score -= 12; reasons.append("Chart line trends downward.")

    # Cross-reference live engine if ticker found
    engine = None
    if ticker and callable(live_engine):
        try:
            engine = live_engine(ticker)
            if engine:
                es = engine.get("score", 50)
                reasons.append(f"Live engine score for {ticker}: {es} ({engine.get('action')}).")
                score = int(0.6 * score + 0.4 * es)
        except Exception:
            engine = None

    score = max(0, min(100, round(score)))
    action = "BUY" if score >= 60 else "SELL" if score <= 38 else "HOLD"
    if not reasons:
        reasons.append("No strong visual/text signal — defaulting to HOLD.")

    return {
        "ok": True,
        "detected_text": text.strip()[:300],
        "ticker": ticker,
        "price": price,
        "pct_change": pct,
        "green_ratio": round(g_ratio, 3),
        "red_ratio": round(r_ratio, 3),
        "trend_slope": round(slope, 3),
        "score": score,
        "action": action,
        "reasons": reasons,
        "engine": engine,
    }
