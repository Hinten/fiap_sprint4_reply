# Use uma imagem base Python
FROM requirements-cache:latest

WORKDIR /app

COPY .env /app/.env
COPY src/ /app/src/
COPY styles/ /app/styles/
COPY main_dash.py /app/main_dash.py
COPY .streamlit /app/.streamlit

# Copy and run the static code generator for Model imports
COPY generators/generate_model_imports.py /app/generators/generate_model_imports.py
RUN python /app/generators/generate_model_imports.py

EXPOSE 8501

CMD ["streamlit", "run", "main_dash.py"]


