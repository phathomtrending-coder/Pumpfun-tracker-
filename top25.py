from ranking import build_top25_boards

def short_money(value) -> str:
    try:
        n = float(value)
        if n >= 1_000_000:
            return f"${n/1_000_000:.2f}M"
        if n >= 1_000:
            return f"${n/1_000:.1f}K"
        return f"${n:,.0f}"
    except Exception:
        return "$0"

def short_pct(value) -> str:
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return "0.0%"

def format_board_lines(tokens: list[dict], window: str) -> list[str]:
    lines = []

    for i, token in enumerate(tokens[:10], start=1):
        symbol = token.get("token_symbol", "UNKNOWN")
        mcap = short_money(token.get("marketCap", 0))
        price_change = short_pct(token.get("priceChange", {}).get(window, 0))
        score = token.get(f"score_{window}", 0)
        liq = short_money(token.get("liquidity", {}).get("usd", 0))

        line = f"{i}. ${symbol} • {mcap} • Liq {liq} • {price_change} • S:{int(score)}"
        lines.append(line)

    return lines

def build_top25_text(tokens: list[dict]) -> dict:
    boards = build_top25_boards(tokens)

    lines_5m = format_board_lines(boards["top25_5m"], "m5")
    lines_1h = format_board_lines(boards["top25_1h"], "h1")
    lines_24h = format_board_lines(boards["top25_24h"], "h24")

    text_5m = (
        "👻 <b>EARLY PHANTOM TOP 25 — 5M HEAT</b>\n\n"
        + "\n".join(lines_5m)
        + "\n\n⚠️ NFA. DYOR."
    )

    text_1h = (
        "👻 <b>EARLY PHANTOM TOP 25 — 1H STRENGTH</b>\n\n"
        + "\n".join(lines_1h)
        + "\n\n⚠️ NFA. DYOR."
    )

    text_24h = (
        "👻 <b>EARLY PHANTOM TOP 25 — 24H WINNERS</b>\n\n"
        + "\n".join(lines_24h)
        + "\n\n⚠️ NFA. DYOR."
    )

    return {
        "boards": boards,
        "text_5m": text_5m,
        "text_1h": text_1h,
        "text_24h": text_24h,
  }
