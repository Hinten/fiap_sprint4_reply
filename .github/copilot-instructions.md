# Copilot Coding Agent Instructions

## Repository Overview

**Project**: FIAP Sprint 4 - Industrial Equipment Predictive Maintenance System  
**Purpose**: Integrated IoT + ML pipeline for monitoring industrial sensors (temperature, vibration, luminosity) on ESP32 devices, storing data in relational databases, training machine learning models with PyCaret, and displaying real-time KPIs and alerts via Streamlit dashboard.

**Repository Size**: ~17MB  
**Primary Language**: Python 3.11.9 (runs on Python 3.12.3+)  
**Key Frameworks**: Streamlit 1.44.1, FastAPI 0.115.12, PyCaret 3.3.2, SQLAlchemy 2.0.40, Pytest 8.4.2  
**Databases**: SQLite (default), PostgreSQL (production), Oracle (optional)  
**Infrastructure**: Docker/Docker Compose, Terraform (AWS deployment)  
**Testing**: 107 passing tests, 6 skipped (optional dependencies)

## Quick Start Commands

### 1. Bootstrap (First Time Setup)
```bash
# Install dependencies (required before any other command)
pip install -r requirements.txt
```
**Time**: ~60-120 seconds  
**Note**: ALWAYS run this first in a fresh environment or after pulling dependency changes.

### 2. Run Tests
```bash
# Run all tests (recommended before making changes)
python -m pytest tests/ -v

# Quick tests only (skip slow tests)
python -m pytest -m 'not slow' -v

# Specific test categories
./tests/run_tests.sh unit          # Unit tests only
./tests/run_tests.sh integration   # Integration tests
./tests/run_tests.sh coverage      # With coverage report
```
**Time**: ~8-15 seconds for all tests  
**Expected Result**: 107 passed, 6 skipped

### 3. Run Dashboard (Main Application)
```bash
streamlit run main_dash.py
```
**Port**: 8501 (default)  
**Time**: ~5-10 seconds to start  
**Access**: http://localhost:8501

### 4. Run API Server
```bash
uvicorn src.api.api_basica:app --host 0.0.0.0 --port 8180
```
**Port**: 8180  
**Access**: http://localhost:8180  
**Note**: API receives sensor data from ESP32 simulations

### 5. Run with Docker
```bash
# Build and run both dashboard and API
docker-compose up --build

# Stop services
docker-compose down
```
**Ports**: Dashboard on ${DASHBOARD_PORT} (default 8501), API on ${API_PORT} (default 8180)

## Environment Configuration

### Required .env Variables
The project uses a `.env` file in the repository root. Default configuration uses SQLite:
```bash
LOGGING_ENABLED=false
ENABLE_API=false
SQL_LITE=true          # Use SQLite (no additional config needed)
```

For PostgreSQL (production):
```bash
SQL_LITE=false
POSTGRE_DB_FROM_ENV=true
POSTGRE_USER=postgres
POSTGRE_PASSWORD=<password>
POSTGRE_DB=<database_name>
POSTGRE_HOST=localhost
POSTGRE_PORT=5432
```

For AWS SNS notifications (optional):
```bash
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_SESSION_TOKEN=<token>
SNS_TOPIC_ARN=<arn>
SNS_REGION=<region>
```

## Project Structure

### Root Directory Files
- **main_dash.py**: Entry point for Streamlit dashboard (`streamlit run main_dash.py`)
- **requirements.txt**: Python dependencies
- **pyproject.toml**: Pytest and coverage configuration
- **docker-compose.yaml**: Multi-service Docker orchestration
- **Dockerfile**: Base Python 3.11 image with dependencies
- **.env**: Environment variables (not committed, see above)
- **deploy_app_server.bat**: AWS EC2 deployment automation script

### Source Code (`src/`)
- **src/api/**: FastAPI server for receiving ESP32 sensor data
  - `api_basica.py`: Main FastAPI app with lifespan management
  - `init_sensor.py`: Endpoint for initializing sensors
  - `receber_leitura.py`: Endpoint for receiving sensor readings
- **src/dashboard/**: Streamlit UI components
  - `main.py`: Dashboard entry point
  - `menu.py`, `navigator.py`: Navigation logic
  - `database/`: DB CRUD views
  - `machine_learning/`: Model training UI
  - `visualizacao_leituras/`: Real-time sensor visualization
  - `notificacoes/`: Email alert system
- **src/database/**: Database layer with SQLAlchemy models
  - `tipos_base/database.py`: Database initialization (SQLite/PostgreSQL/Oracle)
  - `models/`: ORM models (Empresa, Equipamento, Sensor, LeituraSensor, ManutencaoEquipamento, TipoSensor)
- **src/machine_learning/**: ML model training and inference
- **src/wokwi/**: ESP32 simulation code (Arduino/C++)
- **src/logger/**: Logging utilities
- **src/utils/**: Shared utilities

### Tests (`tests/`)
- **tests/unit/**: Unit tests for CRUD, database, validation
- **tests/integration/**: API integration tests
- **tests/crud/**: Model-specific CRUD tests
- **tests/memory/**: Memory leak detection tests
- **tests/run_tests.sh**: Test runner script with multiple modes
- **conftest.py**: Pytest fixtures and configuration

### Infrastructure (`iac/`)
- **iac/dev/**: Terraform configuration for AWS deployment
  - `main.tf`, `variables.tf`, `outputs.tf`, `terraform.tf`

## Common Build/Test Pitfalls

### ✅ ALWAYS install dependencies first
```bash
pip install -r requirements.txt
```
Without this, imports will fail.

### ✅ Database auto-initialization
Database tables are **automatically created** when starting the dashboard or API. You do NOT need to run SQL scripts manually. The schema is defined in `src/database/models/`.

### ✅ Python version compatibility
The project specifies Python 3.11.9 in README but runs fine on Python 3.12.3+. If you encounter dependency issues, use Python 3.11.

### ✅ Test execution
Always run from the repository root:
```bash
python -m pytest tests/
```
NOT `pytest tests/` directly (may cause import issues).

### ✅ Docker build caching
The Dockerfile installs dependencies separately to leverage Docker layer caching. If dependencies change, rebuild with `--no-cache`:
```bash
docker-compose build --no-cache
```

### ✅ Streamlit port conflicts
If port 8501 is in use, Streamlit will auto-select another port. Check terminal output for actual port.

### ✅ ESP32 simulation API URL
When running Wokwi simulation, set `API_URL` in `src/wokwi/.env` to your local machine's network IP (NOT localhost/127.0.0.1):
```bash
API_URL=http://192.168.0.x:8180
```
The ESP32 simulator runs in a separate network context.

## Validation Checklist Before Committing

1. **Run tests**: `python -m pytest tests/ -v` (expect 107 passed, 6 skipped)
2. **Check imports**: Ensure all new modules are importable
3. **Verify .env**: Do NOT commit secrets; ensure `.env` is in `.gitignore`
4. **Database compatibility**: Test with SQLite (default) unless PostgreSQL-specific
5. **Docker build**: If touching dependencies or Dockerfile, verify `docker-compose up --build` succeeds
6. **Lint (optional)**: No automated linter configured, but follow existing code style

## Database Schema (Reference)
The database schema is auto-created from SQLAlchemy models. Key tables:
- **EMPRESA**: Companies managing equipment
- **EQUIPAMENTO**: Monitored industrial equipment
- **TIPO_SENSOR**: Sensor types (temperature, vibration, luminosity)
- **SENSOR**: Individual sensor instances
- **LEITURA_SENSOR**: Timestamped sensor readings
- **MANUTENCAO_EQUIPAMENTO**: Maintenance records and predictions

See `assets/table_creation.ddl` for DDL reference (DO NOT execute manually).

## CI/CD and Deployment

### Local Testing
No GitHub Actions workflows exist. All testing is local via pytest.

### AWS Deployment
Terraform provisions AWS infrastructure (VPC, EC2, RDS). To deploy:
```bash
cd iac/dev
terraform init
terraform apply
```
Then run `deploy_app_server.bat` to copy files and start services on EC2.

**Cost Warning**: AWS deployment incurs charges. Always run `terraform destroy` after testing.

## Key File Locations

- **Main entry point**: `main_dash.py`
- **API entry point**: `src/api/api_basica.py`
- **Database init**: `src/database/tipos_base/database.py`
- **Models**: `src/database/models/*.py`
- **Test config**: `pyproject.toml` (pytest markers, timeouts)
- **Docker config**: `Dockerfile` (base), `src/dashboard/Dockerfile`, `src/api/Dockerfile`
- **Dependencies**: `requirements.txt`

## Known Issues and Workarounds

2. **Test skips**: 6 tests are skipped due to optional dependencies or environment-specific requirements (e.g., Oracle DB, specific API conditions). This is normal.
3. **Firewall for ESP32**: If ESP32 simulator can't reach API, check firewall rules for port 8180.

## Trust These Instructions

These instructions are validated and current. Only perform additional repo-wide searches (grep, find, etc.) if:
- Information here is incomplete for your specific task
- You encounter errors contradicting these instructions
- You're implementing a feature requiring new dependencies or infrastructure

For routine code changes, follow the commands and structure documented above.
