from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routers import chat, uploads, orders

app = FastAPI(title="Natrium IA - Atendimento API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(uploads.router, prefix="/upload", tags=["upload"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
