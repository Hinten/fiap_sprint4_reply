FROM requirements-cache:latest

WORKDIR /app

COPY src/ /app/src/
COPY .env /app/.env
COPY .streamlit /app/.streamlit

# Copy and run the static code generator for Model imports
COPY generators/generate_model_imports.py /app/generators/generate_model_imports.py
RUN python /app/generators/generate_model_imports.py

EXPOSE 8180

CMD ["uvicorn", "src.api.api_basica:app", "--host", "0.0.0.0", "--port", "8180"]


