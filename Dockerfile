FROM python:3.10-slim

WORKDIR /app

# Installa le dipendenze di sistema necessarie per MySQL/PyMySQL
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-client \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copia i requirements dalla cartella backend e installali
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il contenuto della cartella backend nel container
COPY backend/ .

EXPOSE 5000

CMD ["python", "app.py"]