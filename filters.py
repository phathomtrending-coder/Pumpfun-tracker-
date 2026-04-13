from config import (
    WATCHLIST_MIN_MCAP,
    WATCHLIST_MAX_MCAP,
    WATCHLIST_MIN_VOL_5M,
    WATCHLIST_MIN_BUYS_1H,
    PUBLIC_MIN_MCAP,
    PUBLIC_MAX_MCAP,
    PUBLIC_MIN_VOL_5M,
    PUBLIC_MIN_BUYS_1H,
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
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))
    liq_usd = safe_float(token.get("liquidity", {}).get("usd"))

    buy_ratio = buys_1h / max(sells_1h, 1)

    trend_score = 0
    safety_score = 0
    dev_score = 50

    if 6000 <= mcap <= 45000:
        trend_score += 20
    elif 45000 < mcap <= 70000:
        trend_score += 10

    if vol_5m >= 3000:
        trend_score += 20
    elif vol_5m >= 1500:
        trend_score += 14
    elif vol_5m >= 700:
        trend_score += 8

    if vol_1h >= 25000:
        trend_score += 15
    elif vol_1h >= 10000:
        trend_score += 10
    elif vol_1h >= 5000:
        trend_score += 6

    if buys_1h >= 80:
        trend_score += 18
    elif buys_1h >= 40:
        trend_score += 12
    elif buys_1h >= 15:
        trend_score += 6

    if buy_ratio >= 1.75:
        trend_score += 17
    elif buy_ratio >= 1.35:
        trend_score += 11
    elif buy_ratio >= 1.1:
        trend_score += 6

    if buys_1h > sells_1h:
        trend_score += 10

    trend_score = min(100, trend_score)

    if mcap >= 6000:
        safety_score += 15
    if vol_5m >= 700:
        safety_score += 15
    if vol_1h >= 5000:
        safety_score += 10
    if buys_1h >= 15:
        safety_score += 15
    if buys_1h > sells_1h:
        safety_score += 20
    if buy_ratio >= 1.2:
        safety_score += 15
    if sells_1h > 0:
        safety_score += 10

    if liq_usd >= 5000:
        safety_score += 10

    safety_score = min(100, safety_score)

    return {
        "trend_score": trend_score,
        "safety_score": safety_score,
        "dev_score": dev_score,
        "buy_ratio": round(buy_ratio, 2),
    }


def build_rug_dna(token: dict) -> dict:
    mcap = safe_float(token.get("marketCap"))
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))
    liq_usd = safe_float(token.get("liquidity", {}).get("usd"))

    risk_flags = []
    rug_dna_score = 25  # lower is better

    if sells_1h > buys_1h:
        rug_dna_score += 20
        risk_flags.append("sell_pressure")

    if mcap < 5000:
        rug_dna_score += 10
        risk_flags.append("ultra_low_mcap")

    if vol_5m < 300:
        rug_dna_score += 10
        risk_flags.append("thin_volume")

    if buys_1h <= 5:
        rug_dna_score += 10
        risk_flags.append("weak_buy_activity")

    if liq_usd < 4000:
        rug_dna_score += 10
        risk_flags.append("low_liquidity")

    rug_dna_score = max(0, min(100, rug_dna_score))

    return {
        "rug_dna_score": rug_dna_score,
        "risk_flags": risk_flags,
    }


def passes_watchlist_filters(token: dict) -> bool:
    try:
        mcap = safe_float(token.get("marketCap"))
        vol_5m = safe_float(token.get("volume", {}).get("m5"))
        buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))

        if mcap < WATCHLIST_MIN_MCAP:
            return False
        if mcap > WATCHLIST_MAX_MCAP:
            return False
        if vol_5m < WATCHLIST_MIN_VOL_5M:
            return False
        if buys_1h < WATCHLIST_MIN_BUYS_1H:
            return False

        return True
    except Exception:
        return False


def passes_filters(token: dict) -> bool:
    try:
        mcap = safe_float(token.get("marketCap"))
        vol_5m = safe_float(token.get("volume", {}).get("m5"))
        buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
        sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))

        if mcap < PUBLIC_MIN_MCAP:
            return False
        if mcap > PUBLIC_MAX_MCAP:
            return False
        if vol_5m < PUBLIC_MIN_VOL_5M:
            return False
        if buys_1h < PUBLIC_MIN_BUYS_1H:
            return False
        if buys_1h <= sells_1h:
            return False

        scores = build_scores(token)
        rug = build_rug_dna(token)

        if scores["trend_score"] < 55:
            return False
        if scores["safety_score"] < 50:
            return False
        if rug["rug_dna_score"] > 45:
            return False

        return True
    except Exception:
        return False
