# Use uma imagem base Python
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1

#faz isso primeiro para aproveitar o cache do docker, senão demora muito o build toda vez
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY .env /app/.env
COPY src/ /app/src/
COPY main_dash.py /app/main_dash.py
COPY .streamlit /app/.streamlit


EXPOSE 8501

CMD ["streamlit", "run", "main_dash.py"]

