from config import (
    WATCHLIST_MIN_MCAP,
    WATCHLIST_MAX_MCAP,
    WATCHLIST_MIN_VOL_5M,
    WATCHLIST_MIN_VOL_1H,
    WATCHLIST_MIN_BUYS_1H,
    WATCHLIST_MIN_LIQ,
    PUBLIC_MIN_MCAP,
    PUBLIC_MAX_MCAP,
    PUBLIC_MIN_VOL_5M,
    PUBLIC_MIN_VOL_1H,
    PUBLIC_MIN_BUYS_1H,
    PUBLIC_MIN_LIQ,
    PUBLIC_MIN_BUY_SELL_RATIO,
)

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
    liq = safe_float(token.get("liquidity", {}).get("usd"))
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))
    price_change_1h = safe_float(token.get("priceChange", {}).get("h1"))

    buy_ratio = buys_1h / max(sells_1h, 1)

    trend_score = 0
    safety_score = 0
    dev_score = 50

    if 5000 <= mcap <= 90000:
        trend_score += 18
    elif 90000 < mcap <= 150000:
        trend_score += 8

    if liq >= 15000:
        trend_score += 12
    elif liq >= 7000:
        trend_score += 8
    elif liq >= 3000:
        trend_score += 4

    if vol_1h >= 50000:
        trend_score += 22
    elif vol_1h >= 20000:
        trend_score += 16
    elif vol_1h >= 8000:
        trend_score += 10
    elif vol_1h >= 3000:
        trend_score += 5

    if vol_5m >= 3000:
        trend_score += 10
    elif vol_5m >= 1000:
        trend_score += 7
    elif vol_5m >= 200:
        trend_score += 4

    if buys_1h >= 80:
        trend_score += 16
    elif buys_1h >= 30:
        trend_score += 11
    elif buys_1h >= 10:
        trend_score += 6

    if buy_ratio >= 2.0:
        trend_score += 12
    elif buy_ratio >= 1.4:
        trend_score += 9
    elif buy_ratio >= 1.1:
        trend_score += 5

    if price_change_1h >= 100:
        trend_score += 10
    elif price_change_1h >= 30:
        trend_score += 6
    elif price_change_1h > 0:
        trend_score += 3

    trend_score = min(100, trend_score)

    if liq >= 15000:
        safety_score += 20
    elif liq >= 7000:
        safety_score += 15
    elif liq >= 3000:
        safety_score += 8

    if vol_1h >= 12000:
        safety_score += 15
    elif vol_1h >= 5000:
        safety_score += 10

    if buys_1h >= 12:
        safety_score += 10
    if buys_1h > sells_1h:
        safety_score += 15
    if buy_ratio >= 1.2:
        safety_score += 15
    if vol_5m >= 100:
        safety_score += 8
    if mcap >= 6000:
        safety_score += 7

    safety_score = min(100, safety_score)

    return {
        "trend_score": trend_score,
        "safety_score": safety_score,
        "dev_score": dev_score,
        "buy_ratio": round(buy_ratio, 2),
    }

def build_rug_dna(token: dict) -> dict:
    mcap = safe_float(token.get("marketCap"))
    liq = safe_float(token.get("liquidity", {}).get("usd"))
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))

    risk_flags = []
    rug_dna_score = 35

    if sells_1h > buys_1h:
        rug_dna_score += 15
        risk_flags.append("sell_pressure")

    if mcap < 3000:
        rug_dna_score += 10
        risk_flags.append("microcap")

    if liq < 2000:
        rug_dna_score += 15
        risk_flags.append("thin_liquidity")

    if vol_5m < 25 and vol_1h < 2500:
        rug_dna_score += 12
        risk_flags.append("thin_volume")

    if buys_1h <= 3:
        rug_dna_score += 10
        risk_flags.append("weak_buy_activity")

    rug_dna_score = max(0, min(100, rug_dna_score))

    return {
        "rug_dna_score": rug_dna_score,
        "risk_flags": risk_flags,
    }

def passes_watchlist_filters(token: dict) -> bool:
    try:
        mcap = safe_float(token.get("marketCap"))
        liq = safe_float(token.get("liquidity", {}).get("usd"))
        vol_5m = safe_float(token.get("volume", {}).get("m5"))
        vol_1h = safe_float(token.get("volume", {}).get("h1"))
        buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))

        if mcap < WATCHLIST_MIN_MCAP:
            return False
        if mcap > WATCHLIST_MAX_MCAP:
            return False
        if liq < WATCHLIST_MIN_LIQ:
            return False
        if vol_1h < WATCHLIST_MIN_VOL_1H:
            return False
        if vol_5m < WATCHLIST_MIN_VOL_5M and buys_1h < WATCHLIST_MIN_BUYS_1H:
            return False

        return True
    except Exception:
        return False

def passes_public_filters(token: dict) -> bool:
    try:
        mcap = safe_float(token.get("marketCap"))
        liq = safe_float(token.get("liquidity", {}).get("usd"))
        vol_5m = safe_float(token.get("volume", {}).get("m5"))
        vol_1h = safe_float(token.get("volume", {}).get("h1"))
        buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
        sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))

        buy_ratio = buys_1h / max(sells_1h, 1)

        if mcap < PUBLIC_MIN_MCAP:
            return False
        if mcap > PUBLIC_MAX_MCAP:
            return False
        if liq < PUBLIC_MIN_LIQ:
            return False
        if vol_1h < PUBLIC_MIN_VOL_1H:
            return False
        if buys_1h < PUBLIC_MIN_BUYS_1H:
            return False
        if vol_5m < PUBLIC_MIN_VOL_5M:
            return False
        if buy_ratio < PUBLIC_MIN_BUY_SELL_RATIO:
            return False

        scores = build_scores(token)
        if scores["trend_score"] < 32:
            return False
        if scores["safety_score"] < 28:
            return False

        return True
    except Exception:
        return False
