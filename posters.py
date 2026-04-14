import os
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import (
    BOT_TOKEN,
    PUBLIC_CHANNEL_ID,
    WATCHLIST_CHANNEL_ID,
    CHANNEL_LINK,
    PREMIUM_URL,
)
from card_generator import generate_multiplier_card, get_token_logo_url
from top25 import build_top25_text
from filters import pair_age_minutes

bot = Bot(token=BOT_TOKEN)

DEFAULT_LOGO_PATH = os.path.join("assets", "default_token_logo.png")


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


def format_age(token: dict) -> str:
    try:
        mins = int(pair_age_minutes(token))
        if mins < 60:
            return f"{mins}m"
        hours = mins // 60
        rem = mins % 60
        if hours < 24:
            return f"{hours}h {rem}m"
        days = hours // 24
        rem_h = hours % 24
        return f"{days}d {rem_h}h"
    except Exception:
        return "N/A"


def status_text(token: dict) -> str:
    raw = token.get("raw_json", {}) or {}
    labels = [str(x).lower() for x in (raw.get("labels", []) or [])]
    if "graduated" in labels or "bonded" in labels:
        return "Graduated ✅"
    return "Pre-Trend"


def wallet_intel_text(token: dict) -> str:
    buys_1h = token.get("txns", {}).get("h1", {}).get("buys", 0)
    sells_1h = token.get("txns", {}).get("h1", {}).get("sells", 0)

    try:
        buys_1h = int(buys_1h)
        sells_1h = int(sells_1h)
    except Exception:
        buys_1h = 0
        sells_1h = 0

    if buys_1h >= 20 and buys_1h > sells_1h:
        return "Strong early participation"
    if buys_1h >= 8 and buys_1h >= sells_1h:
        return "Healthy early flow"
    if buys_1h >= 3:
        return "Wallets active"
    return "Limited participation"


def bundle_intel_text(token: dict) -> str:
    liq = token.get("liquidity", {}).get("usd", 0)
    vol_1h = token.get("volume", {}).get("h1", 0)

    try:
        liq = float(liq)
        vol_1h = float(vol_1h)
    except Exception:
        liq = 0
        vol_1h = 0

    if liq > 0 and vol_1h > (liq * 8):
        return "Possible heavier clustering"
    if liq > 0 and vol_1h > (liq * 3):
        return "Light cluster"
    return "No major concentration seen"


def build_watchlist_buttons(token: dict):
    buy_url = token.get("pumpfun_url") or token.get("dex_url")
    keyboard = [
        [
            InlineKeyboardButton("🛒 Buy", url=buy_url),
            InlineKeyboardButton("📈 Chart", url=token["dex_url"]),
        ],
        [
            InlineKeyboardButton("👥 Holders", url=token["holders_url"]),
            InlineKeyboardButton("💎 Premium", url=PREMIUM_URL),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_public_alert_buttons(token: dict):
    buy_url = token.get("pumpfun_url") or token.get("dex_url")
    keyboard = [
        [
            InlineKeyboardButton("🛒 Buy", url=buy_url),
            InlineKeyboardButton("📈 Chart", url=token["dex_url"]),
        ],
        [
            InlineKeyboardButton("⚡ Snipe", url=buy_url),
            InlineKeyboardButton("💎 Premium", url=PREMIUM_URL),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_multiplier_buttons(token: dict):
    buy_url = token.get("pumpfun_url") or token.get("dex_url")
    keyboard = [
        [
            InlineKeyboardButton("🛒 Buy", url=buy_url),
            InlineKeyboardButton("📈 Chart", url=token["dex_url"]),
        ],
        [
            InlineKeyboardButton("💎 Premium", url=PREMIUM_URL),
            InlineKeyboardButton("👻 Channel", url=CHANNEL_LINK),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def send_logo_post(chat_id: str, token: dict, caption: str, reply_markup):
    logo_url = get_token_logo_url(token)

    if logo_url:
        try:
            await bot.send_photo(
                chat_id=chat_id,
                photo=logo_url,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            return
        except Exception as e:
            print(f"logo url send failed, using fallback file: {e}")

    try:
        with open(DEFAULT_LOGO_PATH, "rb") as photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
    except Exception as e:
        print(f"default logo send failed: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )


async def post_watchlist_alert(token: dict):
    caption = (
        f"👀 <b>WATCHLIST | ${token['token_symbol']}</b>\n\n"
        f"💠 <b>Token:</b> {token['token_name']}\n"
        f"💰 <b>MCAP:</b> {fmt_money_short(token.get('marketCap', 0))}\n"
        f"💧 <b>Liq:</b> {fmt_money_short(token.get('liquidity', {}).get('usd', 0))}\n"
        f"📊 <b>Buys 1H:</b> {token.get('txns', {}).get('h1', {}).get('buys', 0)} | "
        f"<b>Sells 1H:</b> {token.get('txns', {}).get('h1', {}).get('sells', 0)}\n"
        f"🕒 <b>Age:</b> {format_age(token)}\n"
        f"📈 <b>Status:</b> {status_text(token)}\n"
        f"🧠 <b>Reason:</b> {token.get('reason_posted', 'Pre-trend candidate')}\n\n"
        f"👛 <b>Wallet Intel:</b> {wallet_intel_text(token)}\n"
        f"📦 <b>Bundle Intel:</b> {bundle_intel_text(token)}\n\n"
        f"📋 <b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
        f"💎 Premium gets full heat boards and deeper intel."
    )

    await send_logo_post(
        chat_id=WATCHLIST_CHANNEL_ID,
        token=token,
        caption=caption,
        reply_markup=build_watchlist_buttons(token),
    )


async def post_public_alert(token: dict):
    caption = (
        f"👻 <b>EARLY PHANTOM ENTRY | ${token['token_symbol']}</b>\n\n"
        f"💊 <b>{token['token_name']}</b>\n"
        f"💰 <b>MC:</b> {fmt_money_short(token.get('marketCap', 0))}\n"
        f"💧 <b>Liq:</b> {fmt_money_short(token.get('liquidity', {}).get('usd', 0))}\n"
        f"📊 <b>Buys 1H:</b> {token.get('txns', {}).get('h1', {}).get('buys', 0)} | "
        f"<b>Sells 1H:</b> {token.get('txns', {}).get('h1', {}).get('sells', 0)}\n"
        f"🕒 <b>Age:</b> {format_age(token)}\n"
        f"📈 <b>Status:</b> {status_text(token)}\n"
        f"🧠 <b>Reason:</b> {token.get('reason_posted', 'Pre-trend candidate')}\n\n"
        f"👛 <b>Wallet Intel:</b> {wallet_intel_text(token)}\n"
        f"📦 <b>Bundle Intel:</b> {bundle_intel_text(token)}\n\n"
        f"📋 <b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
        f"💎 Want earlier signals and premium boards? Tap Premium below.\n"
        f"👻 <a href='{CHANNEL_LINK}'>Early Phantom Trenches</a>"
    )

    await send_logo_post(
        chat_id=PUBLIC_CHANNEL_ID,
        token=token,
        caption=caption,
        reply_markup=build_public_alert_buttons(token),
    )


async def post_multiplier_update(token: dict, multiple: float):
    label = milestone_label(multiple)
    card_path = generate_multiplier_card(token, multiple)

    caption = (
        f"📈 <b>${token['token_symbol']} is up {label}</b>\n"
        f"from 👻 Early Phantom Entry\n\n"
        f"{fmt_money_short(token.get('initial_mcap', 0))} → "
        f"{fmt_money_short(token.get('current_mcap', 0))}\n\n"
        f"📋 <b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
        f"💎 Premium gets earlier watchlist signals and deeper intel.\n"
        f"👻 <a href='{CHANNEL_LINK}'>Early Phantom Trenches</a>"
    )

    with open(card_path, "rb") as photo:
        await bot.send_photo(
            chat_id=PUBLIC_CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=build_multiplier_buttons(token),
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
