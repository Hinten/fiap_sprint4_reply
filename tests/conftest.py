"""
Configuração do pytest e fixtures compartilhadas.
"""
import pytest
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """
    Cria um banco de dados SQLite temporário para testes.
    """
    db_dir = tmp_path_factory.mktemp("test_db")
    db_path = db_dir / "test_database.db"
    return str(db_path)


@pytest.fixture(scope="function")
def test_database(test_db_path):
    """
    Fixture que fornece uma instância de Database configurada para testes.
    Limpa o banco após cada teste.
    """
    from src.database.tipos_base.database import Database
    
    # Configura o banco de testes
    Database.init_sqlite(test_db_path)
    Database.create_all_tables(drop_if_exists=True)
    
    yield Database
    
    # Limpa após o teste
    try:
        Database.drop_all_tables()
    except Exception:
        pass


@pytest.fixture(scope="function")
def db_session(test_database):
    """
    Fornece uma sessão de banco de dados para testes.
    """
    with test_database.get_session() as session:
        yield session


@pytest.fixture
def clean_env():
    """
    Fixture que limpa e restaura variáveis de ambiente.
    """
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
