# Use uma imagem base Python
FROM requirements-cache:latest

WORKDIR /app

COPY .env /app/.env
COPY src/ /app/src/
COPY main_dash.py /app/main_dash.py
COPY .streamlit /app/.streamlit

# Copy and run the static code generator for Model imports
COPY tools/generate_model_imports.py /app/tools/generate_model_imports.py
RUN python /app/tools/generate_model_imports.py

EXPOSE 8501

CMD ["streamlit", "run", "main_dash.py"]


