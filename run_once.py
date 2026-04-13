import asyncio
from tracker import fetch_pairs, normalize_pair
from filters import passes_watchlist_filters, passes_public_filters, build_rug_dna
from bot import scan_for_new_tokens, check_updates

async def main():
    pairs = fetch_pairs()
    print(f"DEBUG raw pairs fetched: {len(pairs)}")

    watchlist_pass = 0
    public_pass = 0
    rug_pass = 0

    for pair in pairs[:100]:
        token = normalize_pair(pair)

        if passes_watchlist_filters(token):
            watchlist_pass += 1

        if passes_public_filters(token):
            public_pass += 1

        rug = build_rug_dna(token)
        if rug["rug_dna_score"] <= 65:
            rug_pass += 1

    print(f"DEBUG watchlist pass count: {watchlist_pass}")
    print(f"DEBUG public pass count: {public_pass}")
    print(f"DEBUG rug pass count: {rug_pass}")

    await scan_for_new_tokens()
    await check_updates()

if __name__ == "__main__":
    asyncio.run(main())
