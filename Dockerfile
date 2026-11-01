FROM python:3.10-slim

WORKDIR /app

# Aggiorna e installa le dipendenze usando default-mysql-client
RUN apt-get update && apt-get install -y \
    build-essential \
    default-mysql-client \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 5000

CMD ["python", "app.py"]