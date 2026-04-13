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

def get_tokens_by_status(status: str):
    result = (
        supabase.table("tracked_tokens")
        .select("*")
        .eq("status", status)
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
