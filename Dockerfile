# Use uma imagem base Python
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copie os arquivos do projeto
COPY /src /app/src
COPY /main_dash.py /app/main_dash.py
COPY /requirements.txt /app/requirements.txt

# Instale as dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Exponha a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "main_dash.py"]

