from fastapi import APIRouter
from ..models.schemas import ChatMessage, ChatResponse
from ..services import rag, openai_client, supabase_client

router = APIRouter()

@router.post("", response_model=ChatResponse)
def chat(msg: ChatMessage):
    # Decide agent if not provided
    agent = msg.agent or ("closure" if msg.order_id else "reception")

    # Retrieve context (RAG)
    retrieved = rag.retrieve_context(msg.text)

    # Build prompt and call OpenAI
    messages = rag.build_messages(agent, msg.text, retrieved)
    reply = openai_client.chat_complete(messages)

    # Persist conversation
    supabase_client.save_message(msg.customer_id, agent, msg.text)
    supabase_client.save_message(msg.customer_id, agent, reply)

    return ChatResponse(reply=reply, agent=agent, order_id=msg.order_id, suggestions=[
        "Enviar receita (foto ou PDF)",
        "Consultar status do pedido",
        "Informar endereço para entrega",
        "Enviar comprovante de pagamento"
    ])
