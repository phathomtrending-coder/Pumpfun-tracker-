from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, PUBLIC_CHANNEL_ID, WATCHLIST_CHANNEL_ID, CHANNEL_LINK
from card_generator import generate_initial_alert_card, generate_multiplier_card

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


async def post_watchlist_alert(token: dict):
    scores = {
        "trend_score": int(token.get("trend_score", 0)),
        "safety_score": int(token.get("safety_score", 0)),
        "dev_score": int(token.get("dev_score", 50)),
        "rug_dna_score": int(token.get("rug_dna_score", 25)),
    }

    card_path = generate_initial_alert_card(token, scores)

    caption = (
        f"👀 <b>WATCHLIST | ${token['token_symbol']}</b>\n\n"
        f"💠 <b>Token:</b> {token['token_name']}\n"
        f"💰 <b>MCAP:</b> {fmt_money_short(token.get('marketCap', 0))}\n"
        f"📡 <b>Trend Score:</b> {scores['trend_score']}/100\n"
        f"🛡️ <b>Safety Score:</b> {scores['safety_score']}/100\n"
        f"🕵️ <b>Dev Score:</b> {scores['dev_score']}/100\n"
        f"🧬 <b>Rug DNA:</b> {scores['rug_dna_score']}/100\n\n"
        f"📋 <b>CA:</b>\n<code>{token['contract_address']}</code>"
    )

    buy_url = token.get("pumpfun_url") or token.get("dex_url")
    keyboard = [
        [
            InlineKeyboardButton("🛒 Buy", url=buy_url),
            InlineKeyboardButton("📈 Chart", url=token["dex_url"]),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    with open(card_path, "rb") as photo:
        await bot.send_photo(
            chat_id=WATCHLIST_CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=markup,
        )


async def post_public_alert(token: dict):
    scores = {
        "trend_score": int(token.get("trend_score", 0)),
        "safety_score": int(token.get("safety_score", 0)),
        "dev_score": int(token.get("dev_score", 50)),
        "rug_dna_score": int(token.get("rug_dna_score", 25)),
    }

    card_path = generate_initial_alert_card(token, scores)

    caption = (
        f"🚨 <b>NEW EARLY TRACK | ${token['token_symbol']}</b>\n\n"
        f"💠 <b>Token:</b> {token['token_name']}\n"
        f"💰 <b>MCAP:</b> {fmt_money_short(token.get('marketCap', 0))}\n"
        f"📡 <b>Trend Score:</b> {scores['trend_score']}/100\n"
        f"🛡️ <b>Safety Score:</b> {scores['safety_score']}/100\n"
        f"🕵️ <b>Dev Score:</b> {scores['dev_score']}/100\n"
        f"🧬 <b>Rug DNA:</b> {scores['rug_dna_score']}/100\n\n"
        f"📋 <b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
        f"👻 <a href='{CHANNEL_LINK}'>Early Phantom Trending</a>"
    )

    buy_url = token.get("pumpfun_url") or token.get("dex_url")
    keyboard = [
        [
            InlineKeyboardButton("🛒 Buy", url=buy_url),
            InlineKeyboardButton("📈 Chart", url=token["dex_url"]),
        ],
        [
            InlineKeyboardButton("👻 Channel", url=CHANNEL_LINK),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    with open(card_path, "rb") as photo:
        await bot.send_photo(
            chat_id=PUBLIC_CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=markup,
        )


async def post_multiplier_update(token: dict, multiple: float):
    label = milestone_label(multiple)
    card_path = generate_multiplier_card(token, multiple)

    caption = (
        f"🚀 <b>${token['token_symbol']} HIT {label}</b>\n\n"
        f"💠 <b>Token:</b> {token['token_name']}\n"
        f"💵 <b>Called MC:</b> {fmt_money_short(token.get('initial_mcap', 0))}\n"
        f"🏆 <b>Now MC:</b> {fmt_money_short(token.get('current_mcap', 0))}\n\n"
        f"📡 <b>Trend Score:</b> {int(token.get('trend_score', 0))}/100\n"
        f"🛡️ <b>Safety Score:</b> {int(token.get('safety_score', 0))}/100\n"
        f"🕵️ <b>Dev Score:</b> {int(token.get('dev_score', 50))}/100\n"
        f"🧬 <b>Rug DNA:</b> {int(token.get('rug_dna_score', 25))}/100\n\n"
        f"📋 <b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
        f"👻 <a href='{CHANNEL_LINK}'>Early Phantom Trending</a>"
    )

    buy_url = token.get("pumpfun_url") or token.get("dex_url")
    keyboard = [
        [
            InlineKeyboardButton("🛒 Buy", url=buy_url),
            InlineKeyboardButton("📈 Chart", url=token["dex_url"]),
        ],
        [
            InlineKeyboardButton("👻 Channel", url=CHANNEL_LINK),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    with open(card_path, "rb") as photo:
        await bot.send_photo(
            chat_id=PUBLIC_CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=markup,
        )
