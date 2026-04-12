from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, CHANNEL_ID

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

    text = (
        f"🚨 <b>NOW TRACKING | ${token['token_symbol']}</b>\n\n"
        f"<b>MCAP:</b> ${format_number(token.get('marketCap', 0))}\n"
        f"<b>Name:</b> {token['token_name']}\n\n"
        f"<b>B1H:</b> {buys_1h} | <b>S1H:</b> {sells_1h}\n"
        f"<b>VOL5M:</b> ${format_number(vol_5m)}\n"
        f"<b>VOL1H:</b> ${format_number(vol_1h)}\n\n"
        f"<b>CA:</b>\n<code>{token['contract_address']}</code>"
    )

    keyboard = [[
        InlineKeyboardButton("Chart", url=token["dex_url"]),
        InlineKeyboardButton("Holders", url=token["holders_url"]),
        InlineKeyboardButton("Pump.fun", url=token["pumpfun_url"]),
    ]]
    markup = InlineKeyboardMarkup(keyboard)

    msg = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        parse_mode="HTML",
        reply_markup=markup,
        disable_web_page_preview=True,
    )
    return msg.message_id

async def post_multiplier_update(token: dict, multiple: float):
    text = (
        f"📈 <b>${token['token_symbol']} made {multiple:.1f}x since ATL</b>\n\n"
        f"<b>ATL MCAP:</b> ${format_number(token.get('atl_mcap', 0))}\n"
        f"<b>Current MCAP:</b> ${format_number(token.get('current_mcap', 0))}\n"
        f"<b>CA:</b>\n<code>{token['contract_address']}</code>"
    )

    keyboard = [[InlineKeyboardButton("Chart", url=token["dex_url"])]]
    markup = InlineKeyboardMarkup(keyboard)

    msg = await bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        parse_mode="HTML",
        reply_markup=markup,
        disable_web_page_preview=True,
    )
    return msg.message_id

async def post_test_message():
    msg = await bot.send_message(
        chat_id=CHANNEL_ID,
        text="✅ Early Phantom Trending test post from GitHub Actions",
        disable_web_page_preview=True,
    )
    return msg.message_id
