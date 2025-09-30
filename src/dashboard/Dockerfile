# Use uma imagem base Python
FROM requirements-cache:latest

WORKDIR /app

COPY .env /app/.env
COPY src/ /app/src/
COPY main_dash.py /app/main_dash.py
COPY .streamlit /app/.streamlit


EXPOSE 8501

CMD ["streamlit", "run", "main_dash.py"]

