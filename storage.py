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
