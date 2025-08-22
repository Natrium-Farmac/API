from .routers import chat, uploads, orders
# Importações necessárias do FastAPI e outras bibliotecas
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- Novas importações para RAG e OpenAI ---
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Importações específicas da OpenAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# --- Fim das novas importações ---

# Configura o logger para exibir mensagens no console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Carrega e verifica a OPENAI_API_KEY
openai_api_key_env = os.getenv("OPENAI_API_KEY")
if not openai_api_key_env:
    logging.error("OPENAI_API_KEY não encontrada nas variáveis de ambiente.")
    raise ValueError("OPENAI_API_KEY não encontrada. Por favor, configure-a no arquivo .env.")

# Inicializa o aplicativo FastAPI
app = FastAPI()

# --- Configuração do CORS para permitir requisições do frontend ---
# Para o desenvolvimento local, permitir todas as origens é uma prática comum.
# Em produção, você deve substituir "*" pela URL do seu frontend.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Message(BaseModel):
    message: str 

#Função para carregar, processar e armazenar documentos para RAG
#---------------------------------------------
def load_and_process_documents(directory_path: str):
    """
    Carrega documentos de um diretório, divide-os, cria embeddings
    e os armazena em um vetor store Chroma.
    """
    global vectorstore, retriever, llm, chain  # Declarar como global para modificar

    logging.info(f"Iniciando carregamento e processamento de documentos do diretório: {directory_path}")

    try:
        # 1. Carregar documentos (ex: PDFs)
        documents = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory_path, filename)
                logging.info(f"Carregando PDF: {file_path}")
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
        
        if not documents:
            logging.warning("Nenhum documento PDF encontrado para carregar. O RAG não será ativado.")
            return

        # 2. Dividir documentos em chunks menores
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        logging.info(f"Documentos divididos em {len(splits)} chunks.")

        # 3. Criar embeddings (usando OpenAIEmbeddings)
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key_env)
        logging.info("Embeddings da OpenAI inicializados.")

        # 4. Criar e persistir o vetor store Chroma
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever()
        logging.info("Vector store Chroma criado e retriever configurado.")

        # Inicializa o modelo LLM (usando ChatOpenAI)
        # Você pode especificar outros modelos como "gpt-4" se tiver acesso
        llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key_env)
        logging.info("Modelo OpenAI (gpt-3.5-turbo) inicializado para a cadeia RAG.")

        # Define o prompt do sistema para o chatbot com contexto RAG
        system_prompt = (
            "Você é um assistente de chatbot prestativo e amigável para uma farmácia de manipulação."
            "Seu objetivo é fornecer informações precisas e úteis sobre os serviços da farmácia, produtos,"
            "horários de funcionamento, localização e como enviar receitas."
            "Mantenha as respostas concisas e diretas ao ponto."
            "Use as seguintes informações de contexto para responder à pergunta do usuário. "
            "Se a resposta não estiver no contexto fornecido, diga que você não tem informações sobre isso e peça para o usuário entrar em contato direto com a farmácia."
            "\n\nContexto: {context}"
        )

        # Cria o template do prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", "{user_message}"),
            ]
        )

        # Função auxiliar para combinar documentos
        def combine_documents(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Monta a cadeia RAG
        chain = (
            RunnableParallel(
                context=retriever | combine_documents,
                user_message=RunnablePassthrough()
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        logging.info("Cadeia LangChain RAG configurada.")

    except Exception as e:
        logging.error(f"Erro ao carregar e processar documentos para RAG: {e}")
        vectorstore = None
        retriever = None
        llm = None
        chain = None
        logging.error("RAG não será funcional devido ao erro de carregamento de documentos.")

# --------------------------------------



app = FastAPI(title="Natrium IA - Atendimento API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
def read_root():
    return {"message": "API is live!"}

@app.post("/chat")
def process_message(message: Message):
    return {"response": f"You said: {message.Message}"}

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(uploads.router, prefix="/upload", tags=["upload"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
