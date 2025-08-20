# Natrium IA Backend (FastAPI)

## Rodando localmente
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
export $(cat backend/.env | xargs)
uvicorn app.main:app --reload
```

## Endpoints
- `GET /health`
- `POST /chat`
- `POST /upload`
- `POST /orders`
- `GET /orders/{order_id}`
- `POST /orders/{order_id}/confirm`
