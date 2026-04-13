from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, PUBLIC_CHANNEL_ID, WATCHLIST_CHANNEL_ID, CHANNEL_LINK
from card_generator import generate_initial_alert_card, generate_multiplier_card
from top25 import build_top25_text

bot = Bot(token=BOT_TOKEN)

def fmt_money_short(value) -> str:
    try:
        n = float(value)
        if n >= 1_000_000:
            return f"${n/1_000_000:.2f}M"
        if n >= 1_000:
            return f"${n/1_000:.1f}K"
        return f"${n:,.0f}"
    except Exception:
        return "$0"

def milestone_label(multiple: float) -> str:
    if multiple >= 10:
        return "10X"
    if multiple >= 5:
        return "5X"
    if multiple >= 3:
        return "3X"
    if multiple >= 2:
        return "2X"
    return "50%"

def build_buttons(token: dict, include_holders: bool = True, public: bool = False):
    buy_url = token.get("pumpfun_url") or token.get("dex_url")

    row1 = [
        InlineKeyboardButton("🛒 Buy", url=buy_url),
        InlineKeyboardButton("📈 Chart", url=token["dex_url"]),
    ]

    row2 = []
    if include_holders:
        row2.append(InlineKeyboardButton("👥 Holders", url=token["holders_url"]))
    if public:
        row2.append(InlineKeyboardButton("👻 Channel", url=CHANNEL_LINK))

    keyboard = [row1]
    if row2:
        keyboard.append(row2)

    return InlineKeyboardMarkup(keyboard)

async def post_watchlist_alert(token: dict):
    scores = {
        "trend_score": int(token.get("trend_score", 0)),
        "safety_score": int(token.get("safety_score", 0)),
        "dev_score": int(token.get("dev_score", 50)),
        "rug_dna_score": int(token.get("rug_dna_score", 50)),
    }

    card_path = generate_initial_alert_card(token, scores)

    risk_flags = token.get("risk_flags", []) or []
    risk_line = ", ".join(risk_flags[:3]) if risk_flags else "None"

    caption = (
        f"👀 <b>WATCHLIST | ${token['token_symbol']}</b>\n\n"
        f"💠 <b>Token:</b> {token['token_name']}\n"
        f"💰 <b>MCAP:</b> {fmt_money_short(token.get('marketCap', 0))}\n"
        f"📡 <b>Trend Score:</b> {scores['trend_score']}/100\n"
        f"🛡️ <b>Safety Score:</b> {scores['safety_score']}/100\n"
        f"🕵️ <b>Dev Score:</b> {scores['dev_score']}/100\n"
        f"🧬 <b>Rug DNA:</b> {scores['rug_dna_score']}/100\n"
        f"⚠️ <b>Risk Flags:</b> {risk_line}\n\n"
        f"📋 <b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
        f"💎 Premium gets full heat boards and deeper intel."
    )

    with open(card_path, "rb") as photo:
        await bot.send_photo(
            chat_id=WATCHLIST_CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=build_buttons(token, include_holders=True, public=False),
        )

async def post_public_alert(token: dict):
    scores = {
        "trend_score": int(token.get("trend_score", 0)),
        "safety_score": int(token.get("safety_score", 0)),
        "dev_score": int(token.get("dev_score", 50)),
        "rug_dna_score": int(token.get("rug_dna_score", 50)),
    }

    card_path = generate_initial_alert_card(token, scores)

    risk_flags = token.get("risk_flags", []) or []
    risk_line = ", ".join(risk_flags[:2]) if risk_flags else "Low"

    caption = (
        f"👻 <b>EARLY PHANTOM ENTRY | ${token['token_symbol']}</b>\n\n"
        f"💊 <b>{token['token_name']}</b>\n"
        f"MC: {fmt_money_short(token.get('marketCap', 0))}\n"
        f"Trend: {scores['trend_score']} | Safety: {scores['safety_score']}\n"
        f"Rug DNA: {scores['rug_dna_score']} | Risk: {risk_line}\n\n"
        f"📋 <b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
        f"💎 Premium gets earlier watchlist boards and deeper token intel.\n"
        f"👻 <a href='{CHANNEL_LINK}'>Early Phantom Trenches</a>"
    )

    with open(card_path, "rb") as photo:
        await bot.send_photo(
            chat_id=PUBLIC_CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=build_buttons(token, include_holders=True, public=True),
        )

async def post_multiplier_update(token: dict, multiple: float):
    label = milestone_label(multiple)
    card_path = generate_multiplier_card(token, multiple)

    caption = (
        f"📈 <b>${token['token_symbol']} is up {label}</b>\n"
        f"from 👻 Early Phantom Entry\n\n"
        f"{fmt_money_short(token.get('initial_mcap', 0))} → {fmt_money_short(token.get('current_mcap', 0))}\n\n"
        f"💎 Premium gets earlier watchlist signals and deeper reports.\n"
        f"👻 <a href='{CHANNEL_LINK}'>Early Phantom Trenches</a>"
    )

    with open(card_path, "rb") as photo:
        await bot.send_photo(
            chat_id=PUBLIC_CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=build_buttons(token, include_holders=False, public=True),
        )

async def post_top25_5m(tokens: list[dict]):
    payload = build_top25_text(tokens)
    await bot.send_message(
        chat_id=WATCHLIST_CHANNEL_ID,
        text=payload["text_5m"],
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

async def post_top25_1h_premium(tokens: list[dict]):
    payload = build_top25_text(tokens)
    await bot.send_message(
        chat_id=WATCHLIST_CHANNEL_ID,
        text=payload["text_1h"],
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

async def post_top25_24h_premium(tokens: list[dict]):
    payload = build_top25_text(tokens)
    await bot.send_message(
        chat_id=WATCHLIST_CHANNEL_ID,
        text=payload["text_24h"],
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

async def post_top25_1h_public(tokens: list[dict]):
    payload = build_top25_text(tokens)
    await bot.send_message(
        chat_id=PUBLIC_CHANNEL_ID,
        text=payload["text_1h"],
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

async def post_top25_24h_public(tokens: list[dict]):
    payload = build_top25_text(tokens)
    await bot.send_message(
        chat_id=PUBLIC_CHANNEL_ID,
        text=payload["text_24h"],
        parse_mode="HTML",
        disable_web_page_preview=True,
        )
