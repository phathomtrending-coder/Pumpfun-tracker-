import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PUBLIC_CHANNEL_ID = os.getenv("PUBLIC_CHANNEL_ID", "")
WATCHLIST_CHANNEL_ID = os.getenv("WATCHLIST_CHANNEL_ID", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "30"))

CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/EarlyPhantomTrending")
PREMIUM_URL = os.getenv("PREMIUM_URL", "https://t.me/+qq8BsdtrV1czZmIx")

# Watchlist = early candidates
WATCHLIST_MIN_AGE_MIN = int(os.getenv("WATCHLIST_MIN_AGE_MIN", "0"))
WATCHLIST_MAX_AGE_MIN = int(os.getenv("WATCHLIST_MAX_AGE_MIN", "120"))
WATCHLIST_MIN_MCAP = float(os.getenv("WATCHLIST_MIN_MCAP", "5000"))
WATCHLIST_MAX_MCAP = float(os.getenv("WATCHLIST_MAX_MCAP", "50000"))
WATCHLIST_MIN_LIQ = float(os.getenv("WATCHLIST_MIN_LIQ", "3000"))
WATCHLIST_MIN_VOL_1H = float(os.getenv("WATCHLIST_MIN_VOL_1H", "2000"))
WATCHLIST_MIN_BUYS_1H = int(os.getenv("WATCHLIST_MIN_BUYS_1H", "3"))
WATCHLIST_MAX_SELL_TO_BUY_RATIO = float(os.getenv("WATCHLIST_MAX_SELL_TO_BUY_RATIO", "1.50"))
WATCHLIST_MIN_PRICE_CHANGE_1H = float(os.getenv("WATCHLIST_MIN_PRICE_CHANGE_1H", "-20"))
WATCHLIST_REQUIRE_SOCIAL_SIGNAL = os.getenv("WATCHLIST_REQUIRE_SOCIAL_SIGNAL", "false").lower() == "true"

# Public = stronger pre-trend / trending-soon
PUBLIC_MIN_AGE_MIN = int(os.getenv("PUBLIC_MIN_AGE_MIN", "10"))
PUBLIC_MAX_AGE_MIN = int(os.getenv("PUBLIC_MAX_AGE_MIN", "180"))
PUBLIC_MIN_MCAP = float(os.getenv("PUBLIC_MIN_MCAP", "8000"))
PUBLIC_MAX_MCAP = float(os.getenv("PUBLIC_MAX_MCAP", "60000"))
PUBLIC_MIN_LIQ = float(os.getenv("PUBLIC_MIN_LIQ", "5000"))
PUBLIC_MIN_VOL_1H = float(os.getenv("PUBLIC_MIN_VOL_1H", "6000"))
PUBLIC_MIN_VOL_5M = float(os.getenv("PUBLIC_MIN_VOL_5M", "400"))
PUBLIC_MIN_BUYS_1H = int(os.getenv("PUBLIC_MIN_BUYS_1H", "8"))
PUBLIC_MIN_BUY_SELL_RATIO = float(os.getenv("PUBLIC_MIN_BUY_SELL_RATIO", "1.10"))
PUBLIC_MIN_PRICE_CHANGE_1H = float(os.getenv("PUBLIC_MIN_PRICE_CHANGE_1H", "-5"))
PUBLIC_REQUIRE_SOCIAL_SIGNAL = os.getenv("PUBLIC_REQUIRE_SOCIAL_SIGNAL", "false").lower() == "true"

# Scoring
PRETREND_MIN_SCORE_PUBLIC = int(os.getenv("PRETREND_MIN_SCORE_PUBLIC", "55"))
PRETREND_MIN_SCORE_WATCHLIST = int(os.getenv("PRETREND_MIN_SCORE_WATCHLIST", "35"))
