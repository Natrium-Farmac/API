# Arquitetura

- **Frontend (React + Vite + Tailwind)**: UI estilo ChatGPT com chat + upload (PDF/Imagem).
- **Backend (FastAPI)**: endpoints de chat, upload e pedidos. Agentes (Recepção/Fechamento).
- **RAG**: recuperação de contexto (tabela `kb_chunks` no Supabase).
- **Banco (Supabase)**: tabelas `clientes`, `pedidos`, `mensagens`, `kb_chunks`.
- **Automação (n8n)**: orquestra mensagens WhatsApp -> API -> WhatsApp.
