from datetime import datetime, timezone

from tracker import (
    fetch_pairs,
    fetch_pair_by_address,
    fetch_best_pair_for_token,
    normalize_pair,
)
from filters import (
    passes_watchlist_filters,
    passes_public_filters,
    build_scores,
    build_rug_dna,
)
from storage import (
    get_token_by_ca,
    insert_token,
    update_token,
    get_active_tokens,
    get_board_state,
    upsert_board_state,
)
from posters import (
    post_watchlist_alert,
    post_public_alert,
    post_multiplier_update,
    post_top25_5m,
    post_top25_1h_premium,
    post_top25_24h_premium,
    post_top25_1h_public,
    post_top25_24h_public,
)
from ranking import attach_rank_scores


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def choose_highest_new_threshold(multiplier: float, last_posted: float):
    thresholds = [10, 5, 3, 2, 1.5]
    for threshold in thresholds:
        if multiplier >= threshold and last_posted < threshold:
            return threshold
    return None


def minutes_since_iso(ts: str | None) -> float:
    if not ts:
        return 999999
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - dt).total_seconds() / 60
    except Exception:
        return 999999


def should_post_board(board_name: str, cooldown_minutes: int) -> bool:
    state = get_board_state(board_name)
    if not state:
        return True
    last_posted_at = state.get("last_posted_at")
    return minutes_since_iso(last_posted_at) >= cooldown_minutes


def mark_board_posted(board_name: str):
    now_iso = datetime.now(timezone.utc).isoformat()
    upsert_board_state(board_name, now_iso)


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

        if not passes_watchlist_filters(token):
            continue

        scores = build_scores(token)
        rug = build_rug_dna(token)
        current_mcap = safe_float(token.get("marketCap"))

        record = {
            "token_name": token["token_name"],
            "token_symbol": token["token_symbol"],
            "contract_address": token["contract_address"],
            "pair_address": token["pair_address"],
            "dex_url": token["dex_url"],
            "pumpfun_url": token["pumpfun_url"],
            "holders_url": token["holders_url"],
            "status": "watchlist",
            "posted_to_watchlist": True,
            "posted_to_public": False,
            "initial_mcap": current_mcap,
            "atl_mcap": current_mcap,
            "current_mcap": current_mcap,
            "highest_mcap": current_mcap,
            "volume_5m": safe_float(token.get("volume", {}).get("m5")),
            "volume_1h": safe_float(token.get("volume", {}).get("h1")),
            "buys_1h": int(token.get("txns", {}).get("h1", {}).get("buys", 0)),
            "sells_1h": int(token.get("txns", {}).get("h1", {}).get("sells", 0)),
            "last_multiplier_posted": 0,
            "active": True,
            "trend_score": scores["trend_score"],
            "safety_score": scores["safety_score"],
            "dev_score": scores["dev_score"],
            "rug_dna_score": rug["rug_dna_score"],
            "risk_flags": rug["risk_flags"],
            "reason_posted": scores["reason_posted"],
            "raw_json": token["raw_json"],
        }

        try:
            insert_token(record)
            await post_watchlist_alert({**token, **record})
            print(f"Watchlisted: {token['token_symbol']}")
        except Exception as e:
            print(f"scan_for_new_tokens error for {ca}: {e}")


async def check_updates():
    active_tokens = get_active_tokens()
    ranked_tokens = []

    for db_token in active_tokens:
        ca = db_token["contract_address"]
        pair_address = db_token.get("pair_address")

        current_pair = None
        if pair_address:
            current_pair = fetch_pair_by_address(pair_address)

        if not current_pair:
            current_pair = fetch_best_pair_for_token(ca)

        if not current_pair:
            print(f"Could not refresh {db_token['token_symbol']}")
            continue

        current = normalize_pair(current_pair)
        current_mcap = safe_float(current.get("marketCap"))
        initial_mcap = safe_float(db_token.get("initial_mcap", current_mcap))
        atl_mcap = min(safe_float(db_token.get("atl_mcap", current_mcap)), current_mcap)
        highest_mcap = max(safe_float(db_token.get("highest_mcap", 0)), current_mcap)

        scores = build_scores(current)
        rug = build_rug_dna(current)

        updates = {
            "pair_address": current.get("pair_address", db_token.get("pair_address")),
            "dex_url": current.get("dex_url", db_token.get("dex_url")),
            "pumpfun_url": current.get("pumpfun_url", db_token.get("pumpfun_url")),
            "holders_url": current.get("holders_url", db_token.get("holders_url")),
            "current_mcap": current_mcap,
            "atl_mcap": atl_mcap,
            "highest_mcap": highest_mcap,
            "volume_5m": safe_float(current.get("volume", {}).get("m5")),
            "volume_1h": safe_float(current.get("volume", {}).get("h1")),
            "buys_1h": int(current.get("txns", {}).get("h1", {}).get("buys", 0)),
            "sells_1h": int(current.get("txns", {}).get("h1", {}).get("sells", 0)),
            "trend_score": scores["trend_score"],
            "safety_score": scores["safety_score"],
            "dev_score": scores["dev_score"],
            "rug_dna_score": rug["rug_dna_score"],
            "risk_flags": rug["risk_flags"],
            "reason_posted": scores["reason_posted"],
            "raw_json": current["raw_json"],
        }

        merged = {**db_token, **updates, **current}

        try:
            if db_token.get("status") == "watchlist" and not db_token.get("posted_to_public", False):
                if passes_public_filters(current):
                    await post_public_alert(merged)
                    updates["status"] = "promoted"
                    updates["posted_to_public"] = True
                    print(f"Promoted: {db_token['token_symbol']}")

            if db_token.get("status") == "promoted" or updates.get("status") == "promoted":
                multiplier = current_mcap / initial_mcap if initial_mcap > 0 else 0
                last_posted = safe_float(db_token.get("last_multiplier_posted", 0))
                next_threshold = choose_highest_new_threshold(multiplier, last_posted)

                if next_threshold:
                    await post_multiplier_update(merged, next_threshold)
                    updates["last_multiplier_posted"] = next_threshold
                    print(f"Posted milestone {next_threshold} for {db_token['token_symbol']}")

            if current_mcap < max(initial_mcap * 0.25, 1500):
                updates["status"] = "dead"
                updates["active"] = False

            update_token(ca, updates)

            ranked_token = {**merged, "highest_mcap": highest_mcap}
            ranked_tokens.append(attach_rank_scores(ranked_token))

        except Exception as e:
            print(f"check_updates error for {db_token['token_symbol']}: {e}")
            try:
                update_token(ca, updates)
            except Exception as inner:
                print(f"update_token fallback error for {db_token['token_symbol']}: {inner}")

    if ranked_tokens:
        try:
            if should_post_board("top25_5m_premium", 15):
                await post_top25_5m(ranked_tokens)
                mark_board_posted("top25_5m_premium")
                print("Posted premium Top 25 5m")

            if should_post_board("top25_1h_premium", 60):
                await post_top25_1h_premium(ranked_tokens)
                mark_board_posted("top25_1h_premium")
                print("Posted premium Top 25 1h")

            if should_post_board("top25_24h_premium", 720):
                await post_top25_24h_premium(ranked_tokens)
                mark_board_posted("top25_24h_premium")
                print("Posted premium Top 25 24h")

            if should_post_board("top25_1h_public", 180):
                await post_top25_1h_public(ranked_tokens)
                mark_board_posted("top25_1h_public")
                print("Posted public Top 25 1h")

            if should_post_board("top25_24h_public", 1440):
                await post_top25_24h_public(ranked_tokens)
                mark_board_posted("top25_24h_public")
                print("Posted public Top 25 24h")

        except Exception as e:
            print(f"top25 post error: {e}")
