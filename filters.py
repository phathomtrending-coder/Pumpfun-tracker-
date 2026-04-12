from config import MIN_MCAP, MAX_MCAP, MIN_VOL_5M, MIN_BUYS_1H

def passes_filters(token: dict) -> bool:
    try:
        mcap = float(token.get("marketCap") or 0)
        vol_5m = float(token.get("volume", {}).get("m5") or 0)
        buys_1h = int(token.get("txns", {}).get("h1", {}).get("buys") or 0)

        if mcap < MIN_MCAP or mcap > MAX_MCAP:
            return False
        if vol_5m < MIN_VOL_5M:
            return False
        if buys_1h < MIN_BUYS_1H:
            return False

        return True
    except Exception:
        return False
