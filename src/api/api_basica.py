from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.settings import DEBUG
from src.api.init_sensor import init_router
from src.api.receber_leitura import receber_router
import uvicorn
import threading
import os
from src.database.tipos_base.database import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    sql_lite: bool = str(os.environ.get("SQL_LITE", 'false')).lower() == "true"
    oracle_from_env = str(os.environ.get("ORACLE_DB_FROM_ENV", 'false')).lower() == "true"

    if sql_lite:
        Database.init_sqlite()
    elif oracle_from_env:
        user = os.environ.get('ORACLE_USER')
        senha = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        Database.init_oracledb(user, senha, dsn)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(init_router, prefix='/init')
app.include_router(receber_router, prefix='/leitura')


def _print_routes(app):
    for route in app.routes:
        if hasattr(route, "methods"):
            print(f"{list(route.methods)} {route.path}")

def iniciar_api():
    """
    Inicia a API
    """
    if DEBUG:
        _print_routes(app)
    uvicorn.run(app, host="0.0.0.0", port=8180)


def inciar_api_thread_paralelo():
    """
    Inicia a API em uma thread separada.
    Isso permite que a API seja executada em segundo plano enquanto outras tarefas podem ser executadas
    """
    api_thread = threading.Thread(target=iniciar_api, daemon=True)
    api_thread.start()

# if __name__ == "__main__":
#
#     uvicorn.run(app, host="0.0.0.0", port=8180)