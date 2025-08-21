# Backend Dockerfile
# Usa uma imagem base oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos para o contêiner
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da sua aplicação para o contêiner
COPY app /app/app

# Expõe a porta que sua aplicação vai usar (ex: 8000 para FastAPI/Uvicorn, 5000 para Flask)
EXPOSE 8000

# Comando para iniciar o servidor da sua aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
