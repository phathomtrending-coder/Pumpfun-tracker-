from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, CHANNEL_ID, CHANNEL_LINK
from filters import build_scores
from card_generator import generate_initial_alert_card, generate_multiplier_card

bot = Bot(token=BOT_TOKEN)

def format_number(value) -> str:
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return "0"

async def post_new_tracking(token: dict):
    buys_1h = token.get("txns", {}).get("h1", {}).get("buys", 0)
    sells_1h = token.get("txns", {}).get("h1", {}).get("sells", 0)
    vol_5m = token.get("volume", {}).get("m5", 0)
    vol_1h = token.get("volume", {}).get("h1", 0)

    scores = build_scores(token)
    card_path = generate_initial_alert_card(token, scores)

    caption = (
        f"🚨 <b>NOW TRACKING | ${token['token_symbol']}</b>\n\n"
        f"<b>MCAP:</b> ${format_number(token.get('marketCap', 0))}\n"
        f"🟢 <b>Buys 1H:</b> {buys_1h}\n"
        f"🔴 <b>Sells 1H:</b> {sells_1h}\n"
        f"<b>Vol 5M:</b> ${format_number(vol_5m)}\n"
        f"<b>Vol 1H:</b> ${format_number(vol_1h)}\n\n"
        f"📈 <b>Trend Score:</b> {scores['trend_score']}/100\n"
        f"🛡️ <b>Safety Score:</b> {scores['safety_score']}/100\n"
        f"🕵️ <b>Dev Score:</b> {scores['dev_score']}/100\n\n"
        f"<b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
        f"👻 <a href='{CHANNEL_LINK}'>Early Phantom Trending</a>"
    )

    buy_url = token["pumpfun_url"] or token["dex_url"]

    keyboard = [
        [
            InlineKeyboardButton("🛒 Buy", url=buy_url),
            InlineKeyboardButton("📈 Chart", url=token["dex_url"]),
        ],
        [
            InlineKeyboardButton("👥 Holders", url=token["holders_url"]),
            InlineKeyboardButton("👻 Channel", url=CHANNEL_LINK),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    with open(card_path, "rb") as photo:
        msg = await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=markup,
        )
    return msg.message_id

async def post_multiplier_update(token: dict, multiple: float):
    scores = build_scores(token)
    card_path = generate_multiplier_card(token, multiple)

    caption = (
        f"📈 <b>${token['token_symbol']} made {multiple:.1f}x since ATL</b>\n\n"
        f"<b>ATL MCAP:</b> ${format_number(token.get('atl_mcap', 0))}\n"
        f"<b>Current MCAP:</b> ${format_number(token.get('current_mcap', 0))}\n\n"
        f"📈 <b>Trend Score:</b> {scores['trend_score']}/100\n"
        f"🛡️ <b>Safety Score:</b> {scores['safety_score']}/100\n"
        f"🕵️ <b>Dev Score:</b> {scores['dev_score']}/100\n\n"
        f"<b>CA:</b>\n<code>{token['contract_address']}</code>\n\n"
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
        msg = await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=markup,
        )
    return msg.message_id
