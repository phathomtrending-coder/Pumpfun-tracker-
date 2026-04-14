from datetime import datetime, timezone

from config import (
    WATCHLIST_MIN_AGE_MIN,
    WATCHLIST_MAX_AGE_MIN,
    WATCHLIST_MIN_MCAP,
    WATCHLIST_MAX_MCAP,
    WATCHLIST_MIN_LIQ,
    WATCHLIST_MIN_VOL_1H,
    WATCHLIST_MIN_BUYS_1H,
    WATCHLIST_MAX_SELL_TO_BUY_RATIO,
    WATCHLIST_MIN_PRICE_CHANGE_1H,
    WATCHLIST_REQUIRE_SOCIAL_SIGNAL,
    PUBLIC_MIN_AGE_MIN,
    PUBLIC_MAX_AGE_MIN,
    PUBLIC_MIN_MCAP,
    PUBLIC_MAX_MCAP,
    PUBLIC_MIN_LIQ,
    PUBLIC_MIN_VOL_1H,
    PUBLIC_MIN_VOL_5M,
    PUBLIC_MIN_BUYS_1H,
    PUBLIC_MIN_BUY_SELL_RATIO,
    PUBLIC_MIN_PRICE_CHANGE_1H,
    PUBLIC_REQUIRE_SOCIAL_SIGNAL,
    PRETREND_MIN_SCORE_PUBLIC,
    PRETREND_MIN_SCORE_WATCHLIST,
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


def pair_age_minutes(token: dict) -> float:
    try:
        created_ms = token.get("raw_json", {}).get("pairCreatedAt")
        if not created_ms:
            return 999999.0
        created_dt = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - created_dt).total_seconds() / 60
    except Exception:
        return 999999.0


def get_social_signal(token: dict) -> bool:
    raw = token.get("raw_json", {}) or {}
    info = raw.get("info", {}) or {}
    websites = info.get("websites", []) or []
    socials = info.get("socials", []) or []
    image_url = info.get("imageUrl") or raw.get("info", {}).get("imageUrl")
    has_links = len(websites) > 0 or len(socials) > 0
    has_image = bool(image_url)
    return has_links or has_image


def get_buy_sell_ratio(token: dict) -> float:
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))
    return buys_1h / max(sells_1h, 1)


def get_sell_to_buy_ratio(token: dict) -> float:
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))
    return sells_1h / max(buys_1h, 1)


def get_reason_posted(token: dict) -> str:
    age_m = pair_age_minutes(token)
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buy_ratio = get_buy_sell_ratio(token)
    liq = safe_float(token.get("liquidity", {}).get("usd"))
    price_change_1h = safe_float(token.get("priceChange", {}).get("h1"))
    social = get_social_signal(token)

    reasons = []

    if age_m <= 15:
        reasons.append("Fresh launch")
    elif age_m <= 60:
        reasons.append("Early mover")

    if vol_5m >= 1000:
        reasons.append("5m acceleration")
    elif vol_1h >= 10000:
        reasons.append("1h traction")

    if buy_ratio >= 1.5:
        reasons.append("Buy pressure rising")

    if liq >= 10000:
        reasons.append("Healthy liquidity")

    if price_change_1h >= 20:
        reasons.append("Momentum building")

    if social:
        reasons.append("Social signal active")

    return " • ".join(reasons[:3]) if reasons else "Pre-trend candidate"


def build_scores(token: dict) -> dict:
    age_m = pair_age_minutes(token)
    mcap = safe_float(token.get("marketCap"))
    liq = safe_float(token.get("liquidity", {}).get("usd"))
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sells_1h = safe_int(token.get("txns", {}).get("h1", {}).get("sells"))
    price_change_5m = safe_float(token.get("priceChange", {}).get("m5"))
    price_change_1h = safe_float(token.get("priceChange", {}).get("h1"))
    buy_ratio = buys_1h / max(sells_1h, 1)
    social = get_social_signal(token)

    pretrend_score = 0

    # Age sweet spot
    if 5 <= age_m <= 120:
        pretrend_score += 16
    elif 0 <= age_m <= 180:
        pretrend_score += 10

    # Market cap sweet spot
    if 5000 <= mcap <= 50000:
        pretrend_score += 14
    elif 3000 <= mcap <= 80000:
        pretrend_score += 8

    # Liquidity
    if liq >= 10000:
        pretrend_score += 14
    elif liq >= 5000:
        pretrend_score += 10
    elif liq >= 3000:
        pretrend_score += 6

    # Volume
    if vol_1h >= 20000:
        pretrend_score += 16
    elif vol_1h >= 8000:
        pretrend_score += 12
    elif vol_1h >= 2000:
        pretrend_score += 6

    if vol_5m >= 2000:
        pretrend_score += 10
    elif vol_5m >= 500:
        pretrend_score += 6
    elif vol_5m >= 150:
        pretrend_score += 3

    # Activity
    if buys_1h >= 20:
        pretrend_score += 10
    elif buys_1h >= 8:
        pretrend_score += 7
    elif buys_1h >= 3:
        pretrend_score += 4

    if buy_ratio >= 1.5:
        pretrend_score += 10
    elif buy_ratio >= 1.1:
        pretrend_score += 6
    elif buy_ratio >= 0.9:
        pretrend_score += 2

    # Price structure
    if price_change_1h >= 25:
        pretrend_score += 8
    elif price_change_1h >= 5:
        pretrend_score += 5
    elif price_change_1h >= -5:
        pretrend_score += 2

    if price_change_5m > 0:
        pretrend_score += 2

    if social:
        pretrend_score += 6

    pretrend_score = min(100, pretrend_score)

    health_score = 0
    if liq >= 5000:
        health_score += 20
    elif liq >= 3000:
        health_score += 12

    if buys_1h > 0:
        health_score += 10
    if buys_1h >= sells_1h:
        health_score += 15
    if vol_1h >= 2000:
        health_score += 15
    if 0 <= age_m <= 180:
        health_score += 10
    if social:
        health_score += 10

    health_score = min(100, health_score)

    return {
        "pretrend_score": pretrend_score,
        "trend_score": pretrend_score,  # compatibility with existing code
        "health_score": health_score,
        "safety_score": health_score,   # compatibility
        "dev_score": 50,                # compatibility placeholder
        "buy_ratio": round(buy_ratio, 2),
        "reason_posted": get_reason_posted(token),
    }


def build_rug_dna(token: dict) -> dict:
    # Compatibility placeholder so bot.py doesn't break.
    # We are no longer using this as the main decision system.
    return {
        "rug_dna_score": 30,
        "risk_flags": [],
    }


def passes_watchlist_filters(token: dict) -> bool:
    age_m = pair_age_minutes(token)
    mcap = safe_float(token.get("marketCap"))
    liq = safe_float(token.get("liquidity", {}).get("usd"))
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    sell_to_buy = get_sell_to_buy_ratio(token)
    price_change_1h = safe_float(token.get("priceChange", {}).get("h1"))
    social = get_social_signal(token)

    if not (WATCHLIST_MIN_AGE_MIN <= age_m <= WATCHLIST_MAX_AGE_MIN):
        return False
    if not (WATCHLIST_MIN_MCAP <= mcap <= WATCHLIST_MAX_MCAP):
        return False
    if liq < WATCHLIST_MIN_LIQ:
        return False
    if vol_1h < WATCHLIST_MIN_VOL_1H:
        return False
    if buys_1h < WATCHLIST_MIN_BUYS_1H:
        return False
    if sell_to_buy > WATCHLIST_MAX_SELL_TO_BUY_RATIO:
        return False
    if price_change_1h < WATCHLIST_MIN_PRICE_CHANGE_1H:
        return False
    if WATCHLIST_REQUIRE_SOCIAL_SIGNAL and not social:
        return False

    score = build_scores(token)
    return score["pretrend_score"] >= PRETREND_MIN_SCORE_WATCHLIST


def passes_public_filters(token: dict) -> bool:
    age_m = pair_age_minutes(token)
    mcap = safe_float(token.get("marketCap"))
    liq = safe_float(token.get("liquidity", {}).get("usd"))
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    buy_ratio = get_buy_sell_ratio(token)
    price_change_1h = safe_float(token.get("priceChange", {}).get("h1"))
    social = get_social_signal(token)

    if not (PUBLIC_MIN_AGE_MIN <= age_m <= PUBLIC_MAX_AGE_MIN):
        return False
    if not (PUBLIC_MIN_MCAP <= mcap <= PUBLIC_MAX_MCAP):
        return False
    if liq < PUBLIC_MIN_LIQ:
        return False
    if vol_1h < PUBLIC_MIN_VOL_1H:
        return False
    if vol_5m < PUBLIC_MIN_VOL_5M:
        return False
    if buys_1h < PUBLIC_MIN_BUYS_1H:
        return False
    if buy_ratio < PUBLIC_MIN_BUY_SELL_RATIO:
        return False
    if price_change_1h < PUBLIC_MIN_PRICE_CHANGE_1H:
        return False
    if PUBLIC_REQUIRE_SOCIAL_SIGNAL and not social:
        return False

    score = build_scores(token)
    return score["pretrend_score"] >= PRETREND_MIN_SCORE_PUBLIC
