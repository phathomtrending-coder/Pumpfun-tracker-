from config import MIN_MCAP, MAX_MCAP, MIN_VOL_5M, MIN_BUYS_1H

def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default

def build_scores(token: dict) -> dict:
    mcap = safe_float(token.get("marketCap"))
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))

    buy_ratio = buys_1h / max(sells_1h, 1)

    trend_score = 0
    safety_score = 0
    dev_score = 50

    # Trend
    if 12000 <= mcap <= 65000:
        trend_score += 20
    elif 65000 < mcap <= 90000:
        trend_score += 10

    if vol_5m >= 2500:
        trend_score += 22
    elif vol_5m >= 1200:
        trend_score += 14
    elif vol_5m >= 800:
        trend_score += 8

    if vol_1h >= 20000:
        trend_score += 15
    elif vol_1h >= 10000:
        trend_score += 10

    if buys_1h >= 80:
        trend_score += 18
    elif buys_1h >= 40:
        trend_score += 12
    elif buys_1h >= 25:
        trend_score += 7

    if buy_ratio >= 1.6:
        trend_score += 15
    elif buy_ratio >= 1.3:
        trend_score += 10
    elif buy_ratio >= 1.12:
        trend_score += 6

    if sells_1h > 0 and buys_1h > sells_1h:
        trend_score += 10

    trend_score = min(100, trend_score)

    # Safety
    if mcap >= 12000:
        safety_score += 20
    if vol_5m >= 1200:
        safety_score += 20
    if vol_1h >= 10000:
        safety_score += 10
    if buys_1h >= 30:
        safety_score += 15
    if buys_1h > sells_1h:
        safety_score += 20
    if buy_ratio >= 1.25:
        safety_score += 15

    safety_score = min(100, safety_score)

    return {
        "trend_score": trend_score,
        "safety_score": safety_score,
        "dev_score": dev_score,
        "buy_ratio": round(buy_ratio, 2),
    }

def passes_filters(token: dict) -> bool:
    try:
        mcap = safe_float(token.get("marketCap"))
        vol_5m = safe_float(token.get("volume", {}).get("m5"))
        vol_1h = safe_float(token.get("volume", {}).get("h1"))
        buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
        sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))

        if mcap < max(MIN_MCAP, 12000):
            return False

        if mcap > min(MAX_MCAP, 90000):
            return False

        if vol_5m < max(MIN_VOL_5M, 1200):
            return False

        if vol_1h < 5000:
            return False

        if buys_1h < max(MIN_BUYS_1H, 25):
            return False

        if sells_1h <= 0:
            return False

        if buys_1h <= sells_1h:
            return False

        buy_ratio = buys_1h / max(sells_1h, 1)
        if buy_ratio < 1.12:
            return False

        scores = build_scores(token)

        if scores["trend_score"] < 60:
            return False

        if scores["safety_score"] < 55:
            return False

        return True
    except Exception:
        return False
