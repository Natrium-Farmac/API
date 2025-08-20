from supabase import create_client
from ..core.config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY)

def save_message(customer_id: str, agent: str, text: str):
    try:
        supabase.table("mensagens").insert({"cliente_id": customer_id, "agente": agent, "texto": text}).execute()
    except Exception as e:
        print("Supabase save_message error:", e)

def create_order(customer_id: str, receita_url: str | None = None) -> str:
    try:
        data = supabase.table("pedidos").insert({"cliente_id": customer_id, "status": "NEW", "receita_url": receita_url}).execute()
        return str(data.data[0]["id"])
    except Exception as e:
        print("Supabase create_order error:", e)
        return ""

def update_order(order_id: str, **fields):
    try:
        supabase.table("pedidos").update(fields).eq("id", order_id).execute()
    except Exception as e:
        print("Supabase update_order error:", e)

def get_order(order_id: str):
    try:
        data = supabase.table("pedidos").select("*").eq("id", order_id).single().execute()
        return data.data
    except Exception as e:
        print("Supabase get_order error:", e)
        return None
