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
WATCHLIST_MIN_MCAP = float(os.getenv("WATCHLIST_MIN_MCAP", "4000"))
WATCHLIST_MAX_MCAP = float(os.getenv("WATCHLIST_MAX_MCAP", "35000"))
WATCHLIST_MIN_VOL_5M = float(os.getenv("WATCHLIST_MIN_VOL_5M", "300"))
WATCHLIST_MIN_BUYS_1H = int(os.getenv("WATCHLIST_MIN_BUYS_1H", "10"))

# Public promotion rules
PUBLIC_MIN_MCAP = float(os.getenv("PUBLIC_MIN_MCAP", "8000"))
PUBLIC_MAX_MCAP = float(os.getenv("PUBLIC_MAX_MCAP", "45000"))
PUBLIC_MIN_VOL_5M = float(os.getenv("PUBLIC_MIN_VOL_5M", "1200"))
PUBLIC_MIN_BUYS_1H = int(os.getenv("PUBLIC_MIN_BUYS_1H", "25"))
