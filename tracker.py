import requests

DEX_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search?q=pump.fun"

def fetch_pairs():
    try:
        response = requests.get(DEX_SEARCH_URL, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data.get("pairs", [])
    except Exception as e:
        print(f"fetch_pairs error: {e}")
        return []

def normalize_pair(pair: dict) -> dict:
    base = pair.get("baseToken", {}) or {}
    txns = pair.get("txns", {}) or {}
    volume = pair.get("volume", {}) or {}

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
        "raw_json": pair,
    }
