# Minimal RAG service: embeds & retrieves FAQ/policies stored in Supabase table `kb_chunks`
# In production, you'd use pgvector or the Supabase Vector store. Here we simulate retrieval by keyword match.
from typing import List
from ..services.supabase_client import supabase

def retrieve_context(query: str, k: int = 5) -> List[str]:
    try:
        # naive: fetch top kb entries containing any keyword (fallback approach)
        words = [w for w in query.lower().split() if len(w) > 3]
        if not words:
            data = supabase.table("kb_chunks").select("text").limit(k).execute()
        else:
            # OR conditions for a few words
            q = supabase.table("kb_chunks").select("text")
            for w in words[:3]:
                q = q.ilike("text", f"%{w}%")
            data = q.limit(k).execute()
        chunks = [row["text"] for row in data.data or []]
        return chunks
    except Exception as e:
        print("RAG retrieve_context error:", e)
        return []

SYSTEM_RECEPTION = (
    "Você é um assistente de chatbot prestativo e amigável para uma farmácia de manipulação."
    "Seu objetivo é fornecer informações precisas e úteis sobre os serviços da farmácia, produtos,"
    "horários de funcionamento, localização e como enviar receitas."
    "Mantenha as respostas concisas e diretas ao ponto."
    "Use as seguintes informações de contexto para responder à pergunta do usuário. "
    "Se a resposta não estiver no contexto fornecido, diga que você não tem informações sobre isso e peça para o usuário entrar em contato direto com a farmácia."
    "\n\nContexto: {context}"
    "Você é a Agente 1 (Recepção) da Farmácia de Manipulação Natrium. "
    "Objetivo: acolher com gentileza, entender a demanda, orientar o envio da receita (foto/PDF) "
    "e criar o pedido inicial. Seja breve, profissional e calorosa. "
    "Se a pessoa não tiver receita, colete informações do medicamento desejado para orientar."
)

SYSTEM_CLOSURE = (
    "Você é a Agente 2 (Fechamento) da Farmácia de Manipulação Natrium. "
    "Objetivo: após o orçamento enviado pela atendente física, tirar dúvidas, coletar dados "
    "(nome completo do paciente, endereço de entrega, forma de pagamento), enviar instruções de pagamento, "
    "validar comprovante e confirmar o fechamento do pedido. Seja objetivo, cordial e claro."
)

def build_messages(agent: str, user_text: str, retrieved: List[str]):
    sys = SYSTEM_RECEPTION if agent == "reception" else SYSTEM_CLOSURE
    context = "\n".join(retrieved) if retrieved else "Sem contexto adicional."
    return [
        {"role": "system", "content": sys + "\nPolíticas/Contexto:\n" + context},
        {"role": "user", "content": user_text},
    ]
