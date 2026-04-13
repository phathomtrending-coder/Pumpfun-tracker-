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

    if 1000 <= mcap <= 500000:
        trend_score += 10

    if liq >= 10000:
        trend_score += 10
    elif liq >= 3000:
        trend_score += 6
    elif liq >= 500:
        trend_score += 3

    if vol_1h >= 20000:
        trend_score += 18
    elif vol_1h >= 5000:
        trend_score += 10
    elif vol_1h >= 1000:
        trend_score += 5

    if vol_5m >= 1000:
        trend_score += 8
    elif vol_5m >= 100:
        trend_score += 4

    if buys_1h >= 20:
        trend_score += 12
    elif buys_1h >= 5:
        trend_score += 6
    elif buys_1h >= 1:
        trend_score += 2

    if buy_ratio >= 1.5:
        trend_score += 8
    elif buy_ratio >= 1.0:
        trend_score += 4

    if price_change_1h > 0:
        trend_score += 5

    trend_score = min(100, trend_score)

    if liq >= 10000:
        safety_score += 15
    elif liq >= 3000:
        safety_score += 10
    elif liq >= 500:
        safety_score += 5

    if vol_1h >= 1000:
        safety_score += 10
    if buys_1h >= 1:
        safety_score += 5
    if buy_ratio >= 1.0:
        safety_score += 8
    if mcap >= 1500:
        safety_score += 5

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
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))

    risk_flags = []
    rug_dna_score = 30

    if sells_1h > buys_1h:
        rug_dna_score += 10
        risk_flags.append("sell_pressure")

    if mcap < 1000:
        rug_dna_score += 8
        risk_flags.append("microcap")

    if liq < 500:
        rug_dna_score += 15
        risk_flags.append("thin_liquidity")

    if vol_1h < 500:
        rug_dna_score += 10
        risk_flags.append("thin_volume")

    if buys_1h == 0:
        rug_dna_score += 8
        risk_flags.append("no_buy_activity")

    rug_dna_score = max(0, min(100, rug_dna_score))

    return {
        "rug_dna_score": rug_dna_score,
        "risk_flags": risk_flags,
    }

def passes_watchlist_filters(token: dict) -> bool:
    try:
        mcap = safe_float(token.get("marketCap"))
        liq = safe_float(token.get("liquidity", {}).get("usd"))

        if mcap < WATCHLIST_MIN_MCAP:
            return False
        if mcap > WATCHLIST_MAX_MCAP:
            return False
        if liq < WATCHLIST_MIN_LIQ:
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
        if scores["trend_score"] < 10:
            return False
        if scores["safety_score"] < 8:
            return False

        return True
    except Exception:
        return False
