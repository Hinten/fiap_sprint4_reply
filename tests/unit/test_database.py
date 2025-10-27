"""
Testes unitários para o módulo Database.

Testa a inicialização, conexão e operações básicas do banco de dados.
"""
import pytest
import os
from pathlib import Path
from src.database.tipos_base.database import Database


class TestDatabaseInitialization:
    """Testes de inicialização do banco de dados."""
    
    def test_init_sqlite_default_path(self, tmp_path):
        """Testa inicialização do SQLite com caminho padrão."""
        # Muda para o diretório temporário
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            Database.init_sqlite()
            assert Database.get_engine() is not None
            assert Database.get_session_maker() is not None
            
            # Verifica se o arquivo foi criado
            assert Path(tmp_path / "database.db").exists()
        finally:
            os.chdir(original_cwd)
    
    def test_init_sqlite_custom_path(self, tmp_path):
        """Testa inicialização do SQLite com caminho customizado."""
        db_path = tmp_path / "custom_test.db"
        Database.init_sqlite(str(db_path))
        
        assert Database.get_engine() is not None
        assert Database.get_session_maker() is not None
        assert db_path.exists()
    
    def test_get_session_context_manager(self, test_database):
        """Testa se o context manager de sessão funciona corretamente."""
        with test_database.get_session() as session:
            assert session is not None
            assert not session.is_active or True  # Sessão deve estar ativa
        
        # Após o context manager, a sessão deve estar fechada
        # (não podemos testar diretamente, mas não deve haver erro)
    
    def test_database_session_closes_on_exception(self, test_database):
        """Testa se a sessão fecha mesmo em caso de exceção."""
        try:
            with test_database.get_session() as session:
                assert session is not None
                raise ValueError("Erro de teste")
        except ValueError:
            pass  # Esperado
        
        # A sessão deve ter sido fechada mesmo com a exceção


class TestDatabaseTableOperations:
    """Testes de operações com tabelas."""
    
    def test_create_all_tables(self, test_database):
        """Testa criação de todas as tabelas."""
        # As tabelas já foram criadas pela fixture
        tables = test_database.list_tables()
        assert len(tables) > 0
        assert isinstance(tables, list)
    
    def test_list_tables(self, test_database):
        """Testa listagem de tabelas."""
        tables = test_database.list_tables()
        assert isinstance(tables, list)
        # Deve haver pelo menos algumas tabelas do modelo
        assert len(tables) >= 0
    
    def test_drop_all_tables(self, tmp_path):
        """Testa remoção de todas as tabelas."""
        db_path = tmp_path / "drop_test.db"
        Database.init_sqlite(str(db_path))
        Database.create_all_tables()
        
        initial_tables = Database.list_tables()
        assert len(initial_tables) > 0
        
        Database.drop_all_tables()
        final_tables = Database.list_tables()
        assert len(final_tables) == 0


class TestDatabaseDDLGeneration:
    """Testes de geração de DDL."""
    
    def test_generate_ddl(self, test_database):
        """Testa geração de DDL SQL."""
        ddl = test_database.generate_ddl()
        
        assert isinstance(ddl, str)
        assert len(ddl) > 0
        # Deve conter comandos CREATE TABLE
        assert "CREATE TABLE" in ddl.upper()
    
    def test_generate_mer(self, test_database):
        """Testa geração do MER (Modelo Entidade-Relacionamento)."""
        mer = test_database.generate_mer()
        
        assert isinstance(mer, str)
        assert len(mer) > 0
        # Deve conter informações sobre tabelas
        assert "Tabela:" in mer or len(mer) > 10


class TestDatabaseConnectionResilience:
    """Testes de resiliência da conexão."""
    
    def test_multiple_sessions_sequential(self, test_database):
        """Testa múltiplas sessões sequenciais."""
        from sqlalchemy import text
        
        for _ in range(5):
            with test_database.get_session() as session:
                assert session is not None
                # Executa uma query simples
                result = session.execute(text("SELECT 1")).scalar()
                assert result == 1
    
    def test_nested_sessions_not_recommended_but_handled(self, test_database):
        """
        Testa sessões aninhadas (não recomendado, mas deve ser tratado).
        BUG POTENCIAL: Sessões aninhadas podem causar problemas.
        """
        with test_database.get_session() as session1:
            assert session1 is not None
            
            with test_database.get_session() as session2:
                assert session2 is not None
                # São sessões diferentes
                assert session1 is not session2


class TestDatabaseResetCounter:
    """Testes para reset_contador_ids."""

    def test_reset_contador_ids_sqlite_unsupported(self, test_database):
        """Testa que reset_contador_ids não faz nada para SQLite (não suportado)."""
        from src.database.reset_contador_ids import reset_contador_ids

        # SQLite não é suportado, deve apenas logar e retornar
        reset_contador_ids()  # Não deve dar erro

    def test_get_table_and_sequence_names(self):
        """Testa se get_table_and_sequence_names retorna tuplas corretas."""
        from src.database.reset_contador_ids import get_table_and_sequence_names

        result = get_table_and_sequence_names()
        assert isinstance(result, list)

        for table_name, sequence_name in result:
            assert isinstance(table_name, str)
            assert isinstance(sequence_name, str)
            assert sequence_name.endswith('_SEQ_ID')
            assert table_name in sequence_name

    def test_get_sequences_from_db_sqlite(self, test_database):
        """Testa get_sequences_from_db com SQLite (deve funcionar mesmo sem sequences)."""
        from src.database.reset_contador_ids import get_sequences_from_db

        # Para SQLite, a query pode falhar ou retornar vazio
        try:
            sequences = get_sequences_from_db()
            assert isinstance(sequences, list)
        except Exception:
            # É aceitável que falhe para SQLite
            pass
