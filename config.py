import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

PUBLIC_CHANNEL_ID = os.getenv("PUBLIC_CHANNEL_ID", "")
WATCHLIST_CHANNEL_ID = os.getenv("WATCHLIST_CHANNEL_ID", "")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "30"))

CHANNEL_LINK = "https://t.me/EarlyPhantomTrending"

# Watchlist rules
WATCHLIST_MIN_MCAP = float(os.getenv("WATCHLIST_MIN_MCAP", "1000"))
WATCHLIST_MAX_MCAP = float(os.getenv("WATCHLIST_MAX_MCAP", "150000"))
WATCHLIST_MIN_VOL_5M = float(os.getenv("WATCHLIST_MIN_VOL_5M", "10"))
WATCHLIST_MIN_VOL_1H = float(os.getenv("WATCHLIST_MIN_VOL_1H", "1000"))
WATCHLIST_MIN_BUYS_1H = int(os.getenv("WATCHLIST_MIN_BUYS_1H", "2"))
WATCHLIST_MIN_LIQ = float(os.getenv("WATCHLIST_MIN_LIQ", "1000"))

# Public promotion rules
PUBLIC_MIN_MCAP = float(os.getenv("PUBLIC_MIN_MCAP", "4000"))
PUBLIC_MAX_MCAP = float(os.getenv("PUBLIC_MAX_MCAP", "150000"))
PUBLIC_MIN_VOL_5M = float(os.getenv("PUBLIC_MIN_VOL_5M", "50"))
PUBLIC_MIN_VOL_1H = float(os.getenv("PUBLIC_MIN_VOL_1H", "6000"))
PUBLIC_MIN_BUYS_1H = int(os.getenv("PUBLIC_MIN_BUYS_1H", "8"))
PUBLIC_MIN_LIQ = float(os.getenv("PUBLIC_MIN_LIQ", "3000"))
PUBLIC_MIN_BUY_SELL_RATIO = float(os.getenv("PUBLIC_MIN_BUY_SELL_RATIO", "0.95"))
PUBLIC_MAX_RUG_DNA = int(os.getenv("PUBLIC_MAX_RUG_DNA", "65"))
