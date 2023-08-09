FROM python:3.11-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY init_script.sh init_script.sh
COPY credentials.json credentials.json
COPY client_secret.json client_secret.json
RUN chmod +x init_script.sh
