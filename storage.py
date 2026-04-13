from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "tracked_tokens"


def get_token_by_ca(contract_address: str):
    result = (
        supabase.table(TABLE_NAME)
        .select("*")
        .eq("contract_address", contract_address)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def insert_token(record: dict):
    return supabase.table(TABLE_NAME).insert(record).execute()


def update_token(contract_address: str, updates: dict):
    return (
        supabase.table(TABLE_NAME)
        .update(updates)
        .eq("contract_address", contract_address)
        .execute()
    )


def get_active_tokens():
    result = (
        supabase.table(TABLE_NAME)
        .select("*")
        .eq("active", True)
        .execute()
    )
    return result.data or []
