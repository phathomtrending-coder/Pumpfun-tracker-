import os
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = "assets"
OUTPUT_DIR = "generated_cards"

INITIAL_TEMPLATE = os.path.join(ASSETS_DIR, "initial_alert_base.png")
MULTIPLIER_TEMPLATE = os.path.join(ASSETS_DIR, "multiplier_base.png")
DEFAULT_LOGO = os.path.join(ASSETS_DIR, "default_token_logo.png")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def safe_filename(value: str) -> str:
    return "".join(c for c in value if c.isalnum() or c in ("-", "_")).strip() or "token"


def fmt_money(value) -> str:
    try:
        n = float(value)
        if n >= 1_000_000:
            return f"${n/1_000_000:.2f}M"
        if n >= 1_000:
            return f"${n/1_000:.1f}K"
        return f"${n:,.0f}"
    except Exception:
        return "$0"


def load_font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)

    return ImageFont.load_default()


def download_logo(url: str | None) -> Image.Image:
    if url:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return Image.open(BytesIO(r.content)).convert("RGBA")
        except Exception:
            pass

    return Image.open(DEFAULT_LOGO).convert("RGBA")


def fit_logo_circle(logo: Image.Image, size: int) -> Image.Image:
    logo = logo.copy().convert("RGBA")
    logo.thumbnail((size, size))

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - logo.width) // 2
    y = (size - logo.height) // 2
    canvas.paste(logo, (x, y), logo)

    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size - 1, size - 1), fill=255)

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)
    return out


def get_token_logo_url(token: dict) -> str | None:
    raw = token.get("raw_json", {}) or {}
    info = raw.get("info", {}) or {}

    for key in ["imageUrl", "image_url"]:
        if info.get(key):
            return info.get(key)

    if raw.get("imageUrl"):
        return raw.get("imageUrl")

    return None


def draw_text_block(draw, text, x, y, font, fill, max_width_chars=None, line_spacing=8):
    if max_width_chars:
        lines = textwrap.wrap(text, width=max_width_chars)
    else:
        lines = [text]

    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, current_y), line, font=font)
        current_y += (bbox[3] - bbox[1]) + line_spacing
    return current_y


def generate_initial_alert_card(token: dict, scores: dict) -> str:
    base = Image.open(INITIAL_TEMPLATE).convert("RGBA")
    draw = ImageDraw.Draw(base)

    title_font = load_font(64, bold=True)
    name_font = load_font(32, bold=True)
    body_font = load_font(24, bold=False)
    small_font = load_font(20, bold=False)
    score_font = load_font(22, bold=True)

    logo_url = get_token_logo_url(token)
    logo = download_logo(logo_url)
    logo_circle = fit_logo_circle(logo, 170)
    base.paste(logo_circle, (60, 110), logo_circle)

    symbol = token.get("token_symbol", "UNKNOWN")
    name = token.get("token_name", "Unknown Token")
    ca = token.get("contract_address", "")
    short_ca = f"{ca[:8]}...{ca[-6:]}" if len(ca) > 16 else ca

    mcap = fmt_money(token.get("marketCap", 0))
    buys_1h = token.get("txns", {}).get("h1", {}).get("buys", 0)
    sells_1h = token.get("txns", {}).get("h1", {}).get("sells", 0)
    vol_5m = fmt_money(token.get("volume", {}).get("m5", 0))
    vol_1h = fmt_money(token.get("volume", {}).get("h1", 0))

    draw.text((260, 120), f"${symbol}", font=title_font, fill=(255, 255, 255, 255))
    draw.text((265, 205), short_ca, font=name_font, fill=(215, 215, 215, 255))

    draw.text((70, 370), "NOW TRACKING", font=name_font, fill=(200, 130, 255, 255))

    draw.text((70, 450), f"MCAP {mcap}", font=body_font, fill=(255, 255, 255, 255))
    draw.text((70, 500), f"🟢 Buys 1H: {buys_1h}", font=body_font, fill=(255, 255, 255, 255))
    draw.text((70, 545), f"🔴 Sells 1H: {sells_1h}", font=body_font, fill=(255, 255, 255, 255))
    draw.text((70, 590), f"Vol 5M: {vol_5m}", font=body_font, fill=(255, 255, 255, 255))
    draw.text((70, 635), f"Vol 1H: {vol_1h}", font=body_font, fill=(255, 255, 255, 255))

    draw.text((70, 720), f"Trend Score: {scores['trend_score']}/100", font=score_font, fill=(120, 230, 255, 255))
    draw.text((70, 760), f"Safety Score: {scores['safety_score']}/100", font=score_font, fill=(140, 255, 180, 255))
    draw.text((70, 800), f"Dev Score: {scores['dev_score']}/100", font=score_font, fill=(255, 215, 120, 255))

    draw_text_block(draw, name, 70, 860, body_font, (255, 255, 255, 255), max_width_chars=24)

    out_name = f"{safe_filename(symbol)}_initial.png"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    base.save(out_path)
    return out_path


def generate_multiplier_card(token: dict, multiple: float) -> str:
    base = Image.open(MULTIPLIER_TEMPLATE).convert("RGBA")
    draw = ImageDraw.Draw(base)

    big_font = load_font(110, bold=True)
    title_font = load_font(62, bold=True)
    body_font = load_font(26, bold=False)
    name_font = load_font(30, bold=True)

    logo_url = get_token_logo_url(token)
    logo = download_logo(logo_url)
    logo_circle = fit_logo_circle(logo, 150)
    base.paste(logo_circle, (60, 110), logo_circle)

    symbol = token.get("token_symbol", "UNKNOWN")
    ca = token.get("contract_address", "")
    short_ca = f"{ca[:8]}...{ca[-6:]}" if len(ca) > 16 else ca

    called_mcap = fmt_money(token.get("atl_mcap", 0))
    now_mcap = fmt_money(token.get("current_mcap", 0))

    draw.text((240, 120), f"${symbol}", font=title_font, fill=(255, 255, 255, 255))
    draw.text((245, 205), short_ca, font=name_font, fill=(220, 220, 220, 255))

    draw.text((70, 360), f"{multiple:.1f}X", font=big_font, fill=(180, 120, 255, 255))

    draw.text((70, 710), "Called MC", font=body_font, fill=(255, 255, 255, 255))
    draw.text((70, 760), called_mcap, font=title_font, fill=(255, 255, 255, 255))

    draw.text((390, 710), "Now MC", font=body_font, fill=(255, 255, 255, 255))
    draw.text((390, 760), now_mcap, font=title_font, fill=(255, 255, 255, 255))

    out_name = f"{safe_filename(symbol)}_{int(multiple * 10)}x.png"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    base.save(out_path)
    return out_path
