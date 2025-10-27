from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.settings import DEBUG
from src.api.init_sensor import init_router
from src.api.receber_leitura import receber_router
import uvicorn
import threading
import os
from src.database.tipos_base.database import Database
import atexit
import signal
from src.utils.env_utils import parse_bool_env


@asynccontextmanager
async def lifespan(app: FastAPI):
    sql_lite: bool = parse_bool_env("SQL_LITE")
    oracle = parse_bool_env("ORACLE_DB_FROM_ENV")
    postgre = parse_bool_env("POSTGRE_DB_FROM_ENV")

    if oracle:
        user = os.environ.get('ORACLE_USER')
        senha = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        Database.init_oracledb(user, senha, dsn)
        Database.create_all_tables()
    elif postgre:
        user = os.environ.get('POSTGRE_USER')
        senha = os.environ.get('POSTGRE_PASSWORD')
        database = os.environ.get('POSTGRE_DB')
        host = os.environ.get('POSTGRE_HOST')
        port = os.environ.get('POSTGRE_PORT')
        Database.init_postgresdb(user, senha, host, int(port), database)
        Database.create_all_tables()
    elif sql_lite:
        Database.init_sqlite()
        Database.create_all_tables()
    else:
        print("WARNING: Nenhum banco de dados configurado. Usando SQLite como padrão.")
        Database.init_sqlite()
        Database.create_all_tables()
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


_api_thread = None
_shutdown_event = threading.Event()

def shutdown_api():
    """Desliga a API graciosamente."""
    print("Desligando API...")
    _shutdown_event.set()
    
    if _api_thread is not None:
        if _api_thread.is_alive():
            _api_thread.join(timeout=10)
            if _api_thread.is_alive():
                print("AVISO: API não respondeu ao shutdown em 10 segundos")

def inciar_api_thread_paralelo():
    """
    Inicia a API em uma thread separada com shutdown gracioso.
    """
    global _api_thread

    _api_thread = threading.Thread(target=iniciar_api, daemon=False)
    _api_thread.start()

    # Registra shutdown
    atexit.register(shutdown_api)
    signal.signal(signal.SIGTERM, lambda s, f: shutdown_api())
    signal.signal(signal.SIGINT, lambda s, f: shutdown_api())

# if __name__ == "__main__":
#
#     uvicorn.run(app, host="0.0.0.0", port=8180)