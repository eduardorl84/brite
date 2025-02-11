FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install uv

# Copiar requirements primero para aprovechar la caché de Docker
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Variable de entorno para el puerto (requerida por Cloud Run)
ENV PORT=8000

# Comando para ejecutar la aplicación
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}