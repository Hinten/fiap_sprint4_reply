# Use uma imagem base Python
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/Hinten/fiap_sprint4_reply.git /app/repo

WORKDIR /app/repo

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8180

CMD ["uvicorn", "src.api.api_basica:app", "--host", "0.0.0.0", "--port", "8180"]

