from filters import safe_float, safe_int

def age_bonus_minutes(pair_created_at_ms):
    try:
        if not pair_created_at_ms:
            return 0
        return 10
    except Exception:
        return 0

def compute_score_5m(token: dict) -> float:
    vol_5m = safe_float(token.get("volume", {}).get("m5"))
    buys_5m = safe_int(token.get("txns", {}).get("m5", {}).get("buys"))
    price_change_5m = safe_float(token.get("priceChange", {}).get("m5"))
    liq_usd = safe_float(token.get("liquidity", {}).get("usd"))
    pair_created_at = token.get("raw_json", {}).get("pairCreatedAt")

    score = (
        (vol_5m * 0.28) +
        (buys_5m * 14) +
        (price_change_5m * 7) +
        (liq_usd * 0.06) +
        (age_bonus_minutes(pair_created_at) * 5)
    )
    return round(score, 2)

def compute_score_1h(token: dict) -> float:
    vol_1h = safe_float(token.get("volume", {}).get("h1"))
    buys_1h = safe_int(token.get("txns", {}).get("h1", {}).get("buys"))
    price_change_1h = safe_float(token.get("priceChange", {}).get("h1"))
    liq_usd = safe_float(token.get("liquidity", {}).get("usd"))
    mcap = safe_float(token.get("marketCap"))

    mcap_quality = 0
    if 6000 <= mcap <= 120000:
        mcap_quality = 100
    elif 120000 < mcap <= 200000:
        mcap_quality = 50

    score = (
        (vol_1h * 0.24) +
        (buys_1h * 11) +
        (price_change_1h * 5) +
        (liq_usd * 0.08) +
        mcap_quality
    )
    return round(score, 2)

def compute_score_24h(token: dict) -> float:
    vol_24h = safe_float(token.get("volume", {}).get("h24"))
    buys_24h = safe_int(token.get("txns", {}).get("h24", {}).get("buys"))
    price_change_24h = safe_float(token.get("priceChange", {}).get("h24"))
    liq_usd = safe_float(token.get("liquidity", {}).get("usd"))
    highest_mcap = safe_float(token.get("highest_mcap", token.get("marketCap", 0)))
    current_mcap = safe_float(token.get("marketCap", 0))

    stability_score = 0
    if highest_mcap > 0:
        hold_ratio = current_mcap / highest_mcap
        stability_score = max(0, min(100, hold_ratio * 100))

    score = (
        (vol_24h * 0.18) +
        (buys_24h * 5) +
        (price_change_24h * 4) +
        (liq_usd * 0.07) +
        (stability_score * 4)
    )
    return round(score, 2)

def attach_rank_scores(token: dict) -> dict:
    token = dict(token)
    token["score_5m"] = compute_score_5m(token)
    token["score_1h"] = compute_score_1h(token)
    token["score_24h"] = compute_score_24h(token)
    return token

def build_top25_boards(tokens: list[dict]) -> dict:
    scored = [attach_rank_scores(t) for t in tokens]

    board_5m = sorted(scored, key=lambda x: x.get("score_5m", 0), reverse=True)[:25]
    board_1h = sorted(scored, key=lambda x: x.get("score_1h", 0), reverse=True)[:25]
    board_24h = sorted(scored, key=lambda x: x.get("score_24h", 0), reverse=True)[:25]

    return {
        "top25_5m": board_5m,
        "top25_1h": board_1h,
        "top25_24h": board_24h,
  }
