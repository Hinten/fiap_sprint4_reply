#Imagem separada para a aplicação Python, deixei separada para agilizar o build e fazer o cache das dependências
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1


COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt


