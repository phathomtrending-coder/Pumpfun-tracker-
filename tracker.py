import requests

SEARCH_QUERIES = [
    "pump.fun",
    "pump",
    "solana pump",
]

DEX_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search"
DEX_PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
DEX_TOKEN_PAIRS_URL = "https://api.dexscreener.com/token-pairs/v1/solana/{token_address}"


def fetch_pairs():
    pairs = []
    seen = set()

    for query in SEARCH_QUERIES:
        url = f"{DEX_SEARCH_URL}?q={query}"
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            for pair in data.get("pairs", []):
                pair_address = pair.get("pairAddress")
                if pair_address and pair_address not in seen:
                    seen.add(pair_address)
                    pairs.append(pair)

        except Exception as e:
            print(f"fetch_pairs error for query '{query}': {e}")

    print(f"Fetched {len(pairs)} unique pairs")
    return pairs


def fetch_pair_by_address(pair_address: str):
    try:
        url = DEX_PAIR_URL.format(pair_address=pair_address)
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        pairs = data.get("pairs", []) or []
        return pairs[0] if pairs else None
    except Exception as e:
        print(f"fetch_pair_by_address error for {pair_address}: {e}")
        return None


def fetch_best_pair_for_token(token_address: str):
    try:
        url = DEX_TOKEN_PAIRS_URL.format(token_address=token_address)
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        pairs = response.json() or []

        if not pairs:
            return None

        pairs = sorted(
            pairs,
            key=lambda p: float(p.get("volume", {}).get("h1") or 0),
            reverse=True
        )
        return pairs[0]
    except Exception as e:
        print(f"fetch_best_pair_for_token error for {token_address}: {e}")
        return None


def normalize_pair(pair: dict) -> dict:
    base = pair.get("baseToken", {}) or {}
    txns = pair.get("txns", {}) or {}
    volume = pair.get("volume", {}) or {}
    labels = pair.get("labels", []) or []

    contract_address = base.get("address", "")
    symbol = base.get("symbol", "UNKNOWN")
    name = base.get("name", "Unknown Token")

    dex_url = pair.get("url", "")
    pumpfun_url = f"https://pump.fun/coin/{contract_address}" if contract_address else ""
    holders_url = f"https://solscan.io/token/{contract_address}#holders" if contract_address else ""

    return {
        "token_name": name,
        "token_symbol": symbol,
        "contract_address": contract_address,
        "pair_address": pair.get("pairAddress", ""),
        "dex_url": dex_url,
        "pumpfun_url": pumpfun_url,
        "holders_url": holders_url,
        "marketCap": pair.get("marketCap") or 0,
        "volume": volume,
        "txns": txns,
        "labels": labels,
        "raw_json": pair,
    }
