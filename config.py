import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "30"))
MIN_MCAP = float(os.getenv("MIN_MCAP", "1000"))
MAX_MCAP = float(os.getenv("MAX_MCAP", "500000"))
MIN_VOL_5M = float(os.getenv("MIN_VOL_5M", "100"))
MIN_BUYS_1H = int(os.getenv("MIN_BUYS_1H", "1"))
