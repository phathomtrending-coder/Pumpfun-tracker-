from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_token_by_ca(contract_address: str):
    result = (
        supabase.table("tracked_tokens")
        .select("*")
        .eq("contract_address", contract_address)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

def insert_token(data: dict):
    return supabase.table("tracked_tokens").insert(data).execute()

def update_token(contract_address: str, updates: dict):
    return (
        supabase.table("tracked_tokens")
        .update(updates)
        .eq("contract_address", contract_address)
        .execute()
    )

def get_active_tokens():
    result = (
        supabase.table("tracked_tokens")
        .select("*")
        .eq("active", True)
        .execute()
    )
    return result.data or []

def get_board_state(board_name: str):
    result = (
        supabase.table("board_state")
        .select("*")
        .eq("board_name", board_name)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

def upsert_board_state(board_name: str, last_posted_at: str):
    existing = get_board_state(board_name)
    if existing:
        return (
            supabase.table("board_state")
            .update({"last_posted_at": last_posted_at})
            .eq("board_name", board_name)
            .execute()
        )
    return (
        supabase.table("board_state")
        .insert({"board_name": board_name, "last_posted_at": last_posted_at})
        .execute()
    )

def was_event_posted(token_address: str, event_type: str, destination: str) -> bool:
    result = (
        supabase.table("posted_events")
        .select("id")
        .eq("token_address", token_address)
        .eq("event_type", event_type)
        .eq("destination", destination)
        .limit(1)
        .execute()
    )
    return bool(result.data)

def mark_event_posted(token_address: str, symbol: str, event_type: str, destination: str):
    payload = {
        "token_address": token_address,
        "token_symbol": symbol,
        "event_type": event_type,
        "destination": destination,
    }
    return supabase.table("posted_events").insert(payload).execute()
