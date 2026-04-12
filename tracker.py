import requests

SEARCH_QUERIES = [
    "pump.fun",
    "pump",
    "solana pump",
]

def fetch_pairs():
    pairs = []
    seen = set()

    for query in SEARCH_QUERIES:
        url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
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
    }        "volume": volume,
        "txns": txns,
        "raw_json": pair,
    }
