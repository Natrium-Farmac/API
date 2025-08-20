# Setup

## Requisitos
- Docker + Docker Compose (recomendado)
- Variáveis no `backend/.env`

## Subir tudo
```bash
docker compose up --build
```

## Sem Docker
Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env .env.local  # edite as chaves
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
VITE_API_BASE=http://localhost:8000 npm run dev
```
