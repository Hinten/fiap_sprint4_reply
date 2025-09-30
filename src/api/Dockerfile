FROM requirements-cache:latest

WORKDIR /app

COPY src/ /app/src/
COPY .env /app/.env
COPY .streamlit /app/.streamlit


EXPOSE 8180

CMD ["uvicorn", "src.api.api_basica:app", "--host", "0.0.0.0", "--port", "8180"]

