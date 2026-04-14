import asyncio
from tracker import fetch_pairs, normalize_pair
from filters import passes_watchlist_filters, passes_public_filters, build_scores
from bot import scan_for_new_tokens, check_updates

async def main():
    pairs = fetch_pairs()
    print(f"DEBUG raw pairs fetched: {len(pairs)}")

    watchlist_pass = 0
    public_pass = 0

    for pair in pairs[:200]:
        token = normalize_pair(pair)

        if passes_watchlist_filters(token):
            watchlist_pass += 1
            scores = build_scores(token)
            print(
                "WATCHLIST HIT:",
                token.get("token_symbol"),
                "mcap=", token.get("marketCap"),
                "liq=", token.get("liquidity", {}).get("usd"),
                "vol1h=", token.get("volume", {}).get("h1"),
                "buys1h=", token.get("txns", {}).get("h1", {}).get("buys"),
                "reason=", scores.get("reason_posted"),
                "score=", scores.get("pretrend_score"),
            )

        if passes_public_filters(token):
            public_pass += 1
            scores = build_scores(token)
            print(
                "PUBLIC HIT:",
                token.get("token_symbol"),
                "mcap=", token.get("marketCap"),
                "liq=", token.get("liquidity", {}).get("usd"),
                "vol5m=", token.get("volume", {}).get("m5"),
                "vol1h=", token.get("volume", {}).get("h1"),
                "buys1h=", token.get("txns", {}).get("h1", {}).get("buys"),
                "reason=", scores.get("reason_posted"),
                "score=", scores.get("pretrend_score"),
            )

    print(f"DEBUG watchlist pass count: {watchlist_pass}")
    print(f"DEBUG public pass count: {public_pass}")

    await scan_for_new_tokens()
    await check_updates()

if __name__ == "__main__":
    asyncio.run(main())
