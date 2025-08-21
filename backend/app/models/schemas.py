from pydantic import BaseModel, Field
from typing import Optional, Literal, List

OrderStatus = Literal["NEW","QUOTED","PAYMENT_PENDING","PAID","FULFILLED","CANCELLED"]

class ChatMessage(BaseModel):
    customer_id: str
    text: str
    agent: Optional[Literal["reception","closure"]] = None
    order_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    agent: Literal["reception","closure"]
    order_id: Optional[str] = None
    suggestions: Optional[List[str]] = None

class UploadResponse(BaseModel):
    file_url: str
    type: Literal["image","pdf"]

class OrderCreate(BaseModel):
    customer_id: str
    receita_url: Optional[str] = None

class Order(BaseModel):
    id: str
    customer_id: str
    status: OrderStatus
    valor: Optional[float] = None
    receita_url: Optional[str] = None
    comprovante_url: Optional[str] = None
