from contextlib import contextmanager
from io import StringIO
from typing import Optional
from sqlalchemy import create_engine, Engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import json
import os
from sqlalchemy.sql.ddl import CreateTable
import threading
import tempfile

from src.settings import SQL_ALCHEMY_DEBUG

DEFAULT_DSN = "oracle.fiap.com.br:1521/ORCL"

class Database:

    _engine: Optional[Engine] = None
    _session: Optional[sessionmaker] = None
    _lock = threading.Lock()

    @staticmethod
    def init_sqlite(path:Optional[str] = None):
        """
        Inicializa a conexão com o banco de dados SQLite com validação de tipos e path.
        :param path: Caminho do banco de dados SQLite.
        :return:
        """
        # Validação de tipo
        if path is not None and not isinstance(path, str):
            raise TypeError(f"path deve ser string ou None, não {type(path)}")

        # Validação de valor
        if path is not None and not path.strip():
            raise ValueError("path não pode ser string vazia")

        with Database._lock:
            # Fecha engine antigo se existir
            if Database._engine is not None:
                Database._engine.dispose()

            if path is None:
                path = os.path.join(os.getcwd(), "database.db")

            # Validação básica
            path = os.path.abspath(path)

            # Verifica se não está tentando acessar fora do projeto
            project_root = os.path.abspath(os.getcwd())
            temp_dir = os.path.abspath(tempfile.gettempdir())
            if not (path.startswith(project_root) or path.startswith(temp_dir) or path.startswith('/tmp')):
                raise ValueError(f"Path não permitido: {path}")

            # Verifica se diretório existe ou pode ser criado
            directory = os.path.dirname(path)
            os.makedirs(directory, exist_ok=True)

            Database._engine = create_engine(f"sqlite:///{path}", echo=SQL_ALCHEMY_DEBUG)
            Database._session = sessionmaker(autocommit=False, autoflush=False, bind=Database._engine)

            # Testa a conexão
            with Database._engine.connect() as _:
                print(f"Conexão bem-sucedida ao banco de dados SQLite!\n Path: {path}")

    @staticmethod
    def init_oracledb(user:str, password:str, dsn:str=DEFAULT_DSN):
        '''
        Inicializa a conexão com o banco de dados Oracle.
        :param user: Nome do usuário do banco de dados.
        :param password: Senha do usuário do banco de dados.
        :param dsn: DSN do banco de dados.
        :return:
        '''
        with Database._lock:
            # Fecha engine antigo se existir
            if Database._engine is not None:
                Database._engine.dispose()

            # Cria o engine de conexão
            Database._engine = create_engine(f"oracle+oracledb://{user}:{password}@{dsn}", echo=SQL_ALCHEMY_DEBUG)
            Database._session = sessionmaker(autocommit=False, autoflush=False, bind=Database._engine)

            # Testa a conexão
            with Database._engine.connect() as _:
                print("Conexão bem-sucedida ao banco de dados Oracle!")

    @staticmethod
    def init_postgresdb(user: str, password: str, host: str = "localhost", port: int = 5432, dbname: str = "postgres"):
        """
        Inicializa a conexão com o banco de dados PostgreSQL.
        :param user: Nome do usuário do banco de dados.
        :param password: Senha do usuário do banco de dados.
        :param host: Host do banco de dados.
        :param port: Porta do banco de dados.
        :param dbname: Nome do banco de dados.
        :return:
        """
        with Database._lock:
            # Fecha engine antigo se existir
            if Database._engine is not None:
                Database._engine.dispose()

            Database._engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}", echo=SQL_ALCHEMY_DEBUG)
            Database._session = sessionmaker(autocommit=False, autoflush=False, bind=Database._engine)

            with Database._engine.connect() as _:
                print("Conexão bem-sucedida ao banco de dados PostgreSQL!")

    @staticmethod
    def init_oracledb_from_file(path:str = r"E:\PythonProject\fiap_fase3_cap1\login.json"):

        """
        Inicializa a conexão com o banco de dados Oracle a partir de um arquivo JSON.
        :param path: Caminho do arquivo JSON com as credenciais do banco de dados.
        :return:
        """
        with open(path, "r") as file:
            data = json.load(file)
            user = data["user"]
            password = data["password"]

        Database.init_oracledb(user, password)

    @staticmethod
    def init_with_old_instance(session: sessionmaker, engine: Engine):
        """
        Inicializa a classe Database com uma instância existente de sessionmaker e engine.
        :param session: Instância existente de sessionmaker.
        :param engine: Instância existente de Engine.
        :return:
        """
        with Database._lock:
            Database._session = session
            Database._engine = engine


    @staticmethod
    @contextmanager
    def get_session() -> Generator[Session, None, None]:
        if Database._session is None:
            raise RuntimeError("Database não inicializada. Chame um método init_* primeiro.")
        db = Database._session()
        try:
            yield db
        finally:
            db.close()

    @classmethod
    def list_tables(cls) -> list[str]:
        """
        Lista as tabelas do banco de dados.
        :return: List[str] - Lista com os nomes das tabelas.
        """
        engine = cls._engine
        metadata = MetaData()
        metadata.reflect(bind=engine)
        tables = metadata.tables.keys()
        return list(tables)

    @classmethod
    def list_sequences(cls):
        """
        Lista todas as sequences do banco de dados.
        :return: Lista com os nomes das sequences.
        """
        metadata = MetaData()
        metadata.reflect(bind=cls._engine)
        sequences = [seq.name for seq in metadata._sequences.values()]
        return sequences

    @classmethod
    def create_all_tables(cls, drop_if_exists:bool=False):
        """
            Cria todas as tabelas do banco de dados que herdam de Model.
            ATENÇÃO: Para isso funcionar deve-se carregar todos os models na memória.
            :param drop_if_exists: Se True, remove as tabelas existentes antes de criar novas.
        """

        if drop_if_exists:
            cls.drop_all_tables()

        from src.database.tipos_base.model import Model
        from src.database.dynamic_import import import_models

        import_models(sort=True)

        try:
            Model.metadata.create_all(bind=cls._engine)
            print("Tabelas criadas com sucesso.")
        except Exception as e:
            print("Erro ao criar tabelas no banco de dados.")
            raise

    @classmethod
    def drop_all_tables(cls):
        """
            Dropa todas as tabelas do banco de dados.
            ATENÇÃO: Para isso funcionar deve-se carregar todos os models na memória.
        """
        from src.database.tipos_base.model import Model
        from src.database.dynamic_import import import_models

        import_models(sort=True)

        try:
            Model.metadata.drop_all(bind=cls._engine)
            print("Tabelas removidas com sucesso.")
        except Exception as e:
            print("Erro ao remover tabelas do banco de dados.")
            raise

    @classmethod
    def generate_ddl(cls,) -> str:
        """
        Gera os comandos SQL (DDL) para criar as tabelas baseadas nos models.
        """

        #Os imports são feitos dentro da função para evitar problemas de importação circular.
        from src.database.tipos_base.model import Model
        # É necessário importar os models para que as tabelas sejam criadas corretamente.
        from src.database.dynamic_import import import_models

        import_models(sort=True)

        output = StringIO()

        for table in Model.metadata.sorted_tables:
            ddl_statement = str(CreateTable(table).compile(cls._engine))
            output.write(ddl_statement + ";\n\n")

        return output.getvalue()

    @classmethod
    def generate_mer(cls) -> str:
        """
        Retorna um MER simplificado baseado nos models e relacionamentos declarados.
        """
        #Os imports são feitos dentro da função para evitar problemas de importação circular.
        from src.database.tipos_base.model import Model
        # É necessário importar os models para que as tabelas sejam carregadas corretamente.
        from src.database.dynamic_import import import_models

        import_models(sort=True)
        mer_output = "\nModelo de Entidade-Relacionamento:\n\n"

        for table in Model.metadata.tables.values():
            mer_output += f"Tabela: {table.name}\n"
            for column in table.columns:
                col_info = f"  - {column.name} {f'({column.type} NOT NULL)' if not column.nullable else f'({column.type})'}"
                if column.primary_key:
                    col_info += " [PK]"
                if column.foreign_keys:
                    foreign_table = list(column.foreign_keys)[0].column.table.name
                    col_info += f" [FK -> {foreign_table}]"
                mer_output += col_info + "\n"
            mer_output += "\n"

        return mer_output

    @classmethod
    def get_engine(cls):
        """Método para compatibilidade com testes existentes."""
        return cls._engine

    @classmethod
    def get_session_maker(cls):
        """Método para compatibilidade com testes existentes."""
        return cls._session
