from fastapi import APIRouter, HTTPException
from ..models.schemas import OrderCreate, Order
from ..services import supabase_client
from typing import Optional

router = APIRouter()

@router.post("", response_model=dict)
def create_order(payload: OrderCreate):
    order_id = supabase_client.create_order(payload.customer_id, payload.receita_url)
    if not order_id:
        raise HTTPException(status_code=500, detail="Erro ao criar pedido")
    return {"order_id": order_id}

@router.get("/{order_id}", response_model=dict)
def get_order(order_id: str):
    data = supabase_client.get_order(order_id)
    if not data:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return data

@router.post("/{order_id}/confirm", response_model=dict)
def confirm_payment(order_id: str, comprovante_url: Optional[str] = None):
    supabase_client.update_order(order_id, status="PAID", comprovante_url=comprovante_url)
    return {"status": "PAID"}
