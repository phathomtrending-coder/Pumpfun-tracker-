from tracker import fetch_pairs, normalize_pair
from filters import passes_filters
from storage import get_token_by_ca, insert_token, update_token, get_active_tokens
from posters import post_new_tracking, post_multiplier_update

def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

async def scan_for_new_tokens():
    pairs = fetch_pairs()

    for pair in pairs:
        token = normalize_pair(pair)
        ca = token.get("contract_address")

        if not ca:
            continue

        existing = get_token_by_ca(ca)
        if existing:
            continue

        if not passes_filters(token):
            continue

        try:
            await post_new_tracking(token)

            mcap = safe_float(token.get("marketCap"))
            record = {
                "token_name": token["token_name"],
                "token_symbol": token["token_symbol"],
                "contract_address": token["contract_address"],
                "pair_address": token["pair_address"],
                "dex_url": token["dex_url"],
                "pumpfun_url": token["pumpfun_url"],
                "holders_url": token["holders_url"],
                "alert_posted": True,
                "initial_mcap": mcap,
                "atl_mcap": mcap,
                "current_mcap": mcap,
                "highest_mcap": mcap,
                "volume_5m": safe_float(token.get("volume", {}).get("m5")),
                "volume_1h": safe_float(token.get("volume", {}).get("h1")),
                "buys_1h": int(token.get("txns", {}).get("h1", {}).get("buys", 0)),
                "sells_1h": int(token.get("txns", {}).get("h1", {}).get("sells", 0)),
                "last_multiplier_posted": 0,
                "active": True,
                "raw_json": token["raw_json"],
            }
            insert_token(record)
            print(f"Posted new token: {token['token_symbol']}")

        except Exception as e:
            print(f"scan_for_new_tokens error for {ca}: {e}")

async def check_multipliers():
    active_tokens = get_active_tokens()
    pairs = fetch_pairs()
    by_ca = {}

    for pair in pairs:
        token = normalize_pair(pair)
        ca = token.get("contract_address")
        if ca:
            by_ca[ca] = token

    for db_token in active_tokens:
        ca = db_token["contract_address"]
        current = by_ca.get(ca)

        if not current:
            continue

        current_mcap = safe_float(current.get("marketCap"))
        atl_mcap = min(safe_float(db_token.get("atl_mcap", current_mcap)), current_mcap)
        highest_mcap = max(safe_float(db_token.get("highest_mcap", 0)), current_mcap)

        updates = {
            "current_mcap": current_mcap,
            "atl_mcap": atl_mcap,
            "highest_mcap": highest_mcap,
            "volume_5m": safe_float(current.get("volume", {}).get("m5")),
            "volume_1h": safe_float(current.get("volume", {}).get("h1")),
            "buys_1h": int(current.get("txns", {}).get("h1", {}).get("buys", 0)),
            "sells_1h": int(current.get("txns", {}).get("h1", {}).get("sells", 0)),
            "raw_json": current["raw_json"],
            "pumpfun_url": current.get("pumpfun_url", db_token.get("pumpfun_url")),
            "dex_url": current.get("dex_url", db_token.get("dex_url")),
            "holders_url": current.get("holders_url", db_token.get("holders_url")),
        }

        multiplier = 0
        if atl_mcap > 0:
            multiplier = current_mcap / atl_mcap

        last_posted = safe_float(db_token.get("last_multiplier_posted", 0))
        thresholds = [1.5, 2, 3, 5, 10]

        for threshold in thresholds:
            if multiplier >= threshold and last_posted < threshold:
                merged = {**db_token, **updates}
                try:
                    await post_multiplier_update(merged, threshold)
                    updates["last_multiplier_posted"] = threshold
                    print(f"Posted {threshold}x update for {db_token['token_symbol']}")
                except Exception as e:
                    print(f"multiplier post error: {e}")

        update_token(ca, updates)
