from supabase import create_client, Client
from app.utils.config import SUPABASE_URL, SUPABASE_ANON_KEY

_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def get_client() -> Client:
    return _client


def ping() -> bool:
    _client.table("recipes").select("id").limit(1).execute()
    return True
