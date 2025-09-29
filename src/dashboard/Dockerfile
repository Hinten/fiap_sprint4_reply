# Use uma imagem base Python
FROM python:3.11-slim

WORKDIR /app

#faz isso primeiro para aproveitar o cache do docker, senão demora muito o build toda vez
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY src/ /app/src/
COPY .env /app/.env
COPY main_dash.py /app/main_dash.py


EXPOSE 8501

CMD ["streamlit", "run", "main_dash.py"]

