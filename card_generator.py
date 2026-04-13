import os
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = "assets"
OUTPUT_DIR = "generated_cards"

INITIAL_TEMPLATE = os.path.join(ASSETS_DIR, "initial_alert_base.png")
DEFAULT_LOGO = os.path.join(ASSETS_DIR, "default_token_logo.png")

MILESTONE_TEMPLATES = {
    "50": os.path.join(ASSETS_DIR, "multiplier_50_base.png"),
    "2x": os.path.join(ASSETS_DIR, "multiplier_2x_base.png"),
    "3x": os.path.join(ASSETS_DIR, "multiplier_3x_base.png"),
    "5x": os.path.join(ASSETS_DIR, "multiplier_5x_base.png"),
    "10x": os.path.join(ASSETS_DIR, "multiplier_10x_base.png"),
}

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


def draw_wrapped(draw, text, x, y, font, fill, width_chars=22, line_spacing=8):
    lines = textwrap.wrap(text, width=width_chars) if text else [""]
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, current_y), line, font=font)
        current_y += (bbox[3] - bbox[1]) + line_spacing
    return current_y


def generate_initial_alert_card(token: dict, scores: dict) -> str:
    base = Image.open(INITIAL_TEMPLATE).convert("RGBA")
    draw = ImageDraw.Draw(base)

    title_font = load_font(54, bold=True)
    name_font = load_font(28, bold=True)
    stat_font = load_font(22, bold=True)
    small_font = load_font(18, bold=False)

    logo_url = get_token_logo_url(token)
    logo = download_logo(logo_url)
    logo_circle = fit_logo_circle(logo, 220)
    base.paste(logo_circle, (55, 220), logo_circle)

    symbol = token.get("token_symbol", "UNKNOWN")
    name = token.get("token_name", "Unknown Token")
    ca = token.get("contract_address", "")
    short_ca = f"{ca[:8]}...{ca[-6:]}" if len(ca) > 16 else ca

    mcap = fmt_money(token.get("marketCap", 0))
    buys_1h = token.get("txns", {}).get("h1", {}).get("buys", 0)
    sells_1h = token.get("txns", {}).get("h1", {}).get("sells", 0)
    vol_5m = fmt_money(token.get("volume", {}).get("m5", 0))
    vol_1h = fmt_money(token.get("volume", {}).get("h1", 0))

    draw.text((320, 200), f"${symbol}", font=title_font, fill=(255, 255, 255, 255))
    draw.text((320, 265), short_ca, font=name_font, fill=(220, 220, 220, 255))

    draw.text((320, 355), "MCAP", font=stat_font, fill=(255, 215, 120, 255))
    draw.text((430, 355), mcap, font=stat_font, fill=(255, 255, 255, 255))

    draw.text((320, 405), "BUYS 1H", font=stat_font, fill=(120, 255, 170, 255))
    draw.text((470, 405), str(buys_1h), font=stat_font, fill=(255, 255, 255, 255))

    draw.text((320, 455), "SELLS 1H", font=stat_font, fill=(255, 120, 140, 255))
    draw.text((485, 455), str(sells_1h), font=stat_font, fill=(255, 255, 255, 255))

    draw.text((320, 505), "VOL 5M", font=stat_font, fill=(170, 210, 255, 255))
    draw.text((445, 505), vol_5m, font=stat_font, fill=(255, 255, 255, 255))

    draw.text((320, 555), "VOL 1H", font=stat_font, fill=(170, 210, 255, 255))
    draw.text((445, 555), vol_1h, font=stat_font, fill=(255, 255, 255, 255))

    draw.text((320, 640), "TREND", font=stat_font, fill=(255, 215, 120, 255))
    draw.text((410, 640), f"{scores['trend_score']}/100", font=stat_font, fill=(255, 255, 255, 255))

    draw.text((320, 690), "SAFETY", font=stat_font, fill=(120, 255, 170, 255))
    draw.text((430, 690), f"{scores['safety_score']}/100", font=stat_font, fill=(255, 255, 255, 255))

    draw.text((320, 740), "DEV", font=stat_font, fill=(170, 210, 255, 255))
    draw.text((390, 740), f"{scores['dev_score']}/100", font=stat_font, fill=(255, 255, 255, 255))

    draw_wrapped(draw, name, 320, 800, small_font, (255, 255, 255, 255), width_chars=26)

    out_path = os.path.join(OUTPUT_DIR, f"{safe_filename(symbol)}_initial.png")
    base.save(out_path)
    return out_path


def milestone_key_from_multiple(multiple: float) -> str:
    if multiple >= 10:
        return "10x"
    if multiple >= 5:
        return "5x"
    if multiple >= 3:
        return "3x"
    if multiple >= 2:
        return "2x"
    return "50"


def milestone_label_from_multiple(multiple: float) -> str:
    if multiple >= 10:
        return "10X"
    if multiple >= 5:
        return "5X"
    if multiple >= 3:
        return "3X"
    if multiple >= 2:
        return "2X"
    return "50%"


def generate_multiplier_card(token: dict, multiple: float) -> str:
    milestone_key = milestone_key_from_multiple(multiple)
    template_path = MILESTONE_TEMPLATES[milestone_key]

    base = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(base)

    title_font = load_font(54, bold=True)
    name_font = load_font(28, bold=True)
    stat_font = load_font(22, bold=True)

    logo_url = get_token_logo_url(token)
    logo = download_logo(logo_url)
    logo_circle = fit_logo_circle(logo, 220)
    base.paste(logo_circle, (55, 220), logo_circle)

    symbol = token.get("token_symbol", "UNKNOWN")
    ca = token.get("contract_address", "")
    short_ca = f"{ca[:8]}...{ca[-6:]}" if len(ca) > 16 else ca

    called_mcap = fmt_money(token.get("atl_mcap", 0))
    now_mcap = fmt_money(token.get("current_mcap", 0))
    label = milestone_label_from_multiple(multiple)

    draw.text((320, 200), f"${symbol}", font=title_font, fill=(255, 255, 255, 255))
    draw.text((320, 265), short_ca, font=name_font, fill=(220, 220, 220, 255))

    draw.text((380, 655), "Called MC", font=stat_font, fill=(255, 255, 255, 255))
    draw.text((380, 705), called_mcap, font=title_font, fill=(255, 255, 255, 255))

    draw.text((700, 655), "Now MC", font=stat_font, fill=(255, 255, 255, 255))
    draw.text((700, 705), now_mcap, font=title_font, fill=(255, 255, 255, 255))

    out_path = os.path.join(OUTPUT_DIR, f"{safe_filename(symbol)}_{label.lower().replace('%','pct')}.png")
    base.save(out_path)
    return out_path
