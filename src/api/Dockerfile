# Use uma imagem base Python
FROM python:3.11-slim

WORKDIR /app

#faz isso primeiro para aproveitar o cache do docker, senão demora muito o build toda vez
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY src/ /app/src/
COPY .env /app/.env


EXPOSE 8180

CMD ["uvicorn", "src.api.api_basica:app", "--host", "0.0.0.0", "--port", "8180"]

