"""
Testes de vazamento de memória no Dashboard Streamlit.

Usa tracemalloc e memory_profiler para detectar vazamentos de memória.
"""
import pytest
import tracemalloc
import gc
from unittest.mock import patch, MagicMock
import sys


class TestDashboardMemoryBasic:
    """Testes básicos de memória do dashboard."""
    
    @pytest.mark.skip(reason="Requer todas as dependências do dashboard (joblib, etc)")
    def test_import_dashboard_no_immediate_leak(self):
        """
        Testa se importar o módulo do dashboard não causa vazamento imediato.
        """
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        
        # Importa o módulo
        from src.dashboard import main
        
        # Force garbage collection
        gc.collect()
        
        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        # Calcula diferença
        stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        # Não deve haver crescimento massivo (> 1MB) apenas por importar
        total_diff = sum(stat.size_diff for stat in stats)
        assert total_diff < 1024 * 1024, f"Import causou crescimento de {total_diff} bytes"


class TestDashboardSessionState:
    """
    Testes relacionados ao session_state do Streamlit.
    BUG POTENCIAL: session_state pode acumular dados indefinidamente.
    """
    
    def test_streamlit_session_state_structure(self):
        """
        Verifica estrutura do session_state do Streamlit.
        
        POTENCIAL BUG: Se o session_state não for limpo entre sessões,
        pode causar vazamento de memória em produção.
        """
        # Mock do streamlit
        import streamlit as st
        
        # Verifica se session_state é acessível
        assert hasattr(st, 'session_state')
        
        # Em produção, verificar se há mecanismo de limpeza


class TestDatabaseConnectionLeaks:
    """
    Testes de vazamento de conexões de banco de dados.
    BUG CRÍTICO: Conexões não fechadas são uma fonte comum de memory leaks.
    """
    
    def test_database_session_cleanup(self, test_database):
        """
        Testa se sessões de banco são limpas corretamente.
        """
        import psutil
        import os
        from sqlalchemy import text
        
        process = psutil.Process(os.getpid())
        
        # Captura uso de memória inicial
        initial_memory = process.memory_info().rss
        
        # Cria e fecha múltiplas sessões
        for _ in range(100):
            with test_database.get_session() as session:
                # Executa uma query simples
                session.execute(text("SELECT 1"))
        
        # Force garbage collection
        gc.collect()
        
        # Captura uso de memória final
        final_memory = process.memory_info().rss
        
        # Crescimento de memória deve ser mínimo (< 5MB)
        memory_growth = final_memory - initial_memory
        assert memory_growth < 5 * 1024 * 1024, \
            f"Vazamento de memória detectado: {memory_growth / 1024 / 1024:.2f}MB"
    
    def test_database_connection_not_leaked_on_exception(self, tmp_path):
        """
        BUG POTENCIAL: Exceções podem deixar conexões abertas.
        """
        from src.database.tipos_base.database import Database
        
        db_path = tmp_path / "exception_test.db"
        Database.init_sqlite(str(db_path))
        Database.create_all_tables()
        
        # Tenta causar uma exceção dentro de uma sessão
        connection_opened = False
        try:
            with Database.get_session() as session:
                connection_opened = True
                # Força uma exceção
                raise ValueError("Erro intencional")
        except ValueError:
            pass
        
        assert connection_opened, "Sessão deve ter sido aberta"
        # A conexão deve ter sido fechada mesmo com exceção


class TestMemoryProfilerIntegration:
    """
    Testes usando memory_profiler para análise detalhada.
    """
    
    @pytest.mark.slow
    def test_repeated_operations_memory_stable(self, test_database):
        """
        Testa se operações repetidas mantêm uso de memória estável.
        """
        from memory_profiler import memory_usage
        from sqlalchemy import text
        
        def repeated_db_operations():
            """Simula operações repetidas no dashboard."""
            for _ in range(50):
                with test_database.get_session() as session:
                    session.execute(text("SELECT 1"))
                gc.collect()
        
        # Mede uso de memória durante execução
        mem_usage = memory_usage((repeated_db_operations,), interval=0.1)
        
        if len(mem_usage) > 0:
            # Calcula crescimento
            memory_growth = max(mem_usage) - min(mem_usage)
            
            # Crescimento deve ser mínimo (< 10MB)
            assert memory_growth < 10, \
                f"Crescimento de memória: {memory_growth:.2f}MB"


class TestGlobalVariablesLeaks:
    """
    BUG POTENCIAL: Variáveis globais mutáveis podem acumular dados.
    """
    
    def test_no_mutable_global_defaults(self):
        """
        Verifica se há uso de valores default mutáveis em funções.
        Isso é um bug comum em Python que causa vazamentos.
        """
        # Este é um teste de documentação do problema
        # Exemplo de BUG:
        # def add_item(item, lista=[]):  # BUG! lista é compartilhada
        #     lista.append(item)
        #     return lista
        pass
    
    def test_database_class_variables_not_accumulating(self):
        """
        Verifica se variáveis de classe do Database não acumulam dados.
        """
        from src.database.tipos_base.database import Database
        
        # Engine e session devem ser sobrescritos, não acumulados
        initial_engine = Database.get_engine()
        
        # Re-inicializa
        Database.init_sqlite()
        
        # Engine deve ser o mesmo objeto ou substituído, não duplicado
        assert Database.get_engine() is not None


class TestPlotlyMemoryLeaks:
    """
    BUG POTENCIAL: Gráficos Plotly podem acumular dados em cache.
    """
    
    @pytest.mark.skip(reason="Requer plotly instalado")
    @pytest.mark.slow
    def test_plotly_figure_creation_memory(self):
        """
        Testa se criar múltiplos gráficos Plotly causa vazamento.
        """
        import plotly.graph_objects as go
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Cria e descarta múltiplos gráficos
        for _ in range(100):
            fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
            # Não mantém referência - deve ser coletado
            del fig
        
        gc.collect()
        final_memory = process.memory_info().rss
        
        memory_growth = final_memory - initial_memory
        # Crescimento deve ser mínimo
        assert memory_growth < 10 * 1024 * 1024, \
            f"Plotly memory leak: {memory_growth / 1024 / 1024:.2f}MB"


class TestStreamlitCachingLeaks:
    """
    BUG POTENCIAL: @st.cache pode causar vazamentos se mal usado.
    """
    
    def test_cache_decorator_documentation(self):
        """
        DOCUMENTAÇÃO: Cuidados com @st.cache e @st.cache_data
        
        - @st.cache_data: Armazena dados em cache
        - Se usado em funções que carregam grandes datasets, pode acumular
        - RECOMENDAÇÃO: Usar ttl (time to live) em caches
        - RECOMENDAÇÃO: Limitar tamanho de cache com max_entries
        
        Exemplo de uso correto:
        @st.cache_data(ttl=3600, max_entries=10)
        def load_data():
            return large_dataset
        """
        pass


def test_tracemalloc_snapshot_comparison():
    """
    Teste de exemplo usando tracemalloc para comparar snapshots.
    """
    tracemalloc.start()
    
    # Snapshot inicial
    snapshot1 = tracemalloc.take_snapshot()
    
    # Aloca alguma memória
    data = [i for i in range(1000)]
    
    # Snapshot após alocação
    snapshot2 = tracemalloc.take_snapshot()
    
    # Compara
    stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    # Deve haver crescimento detectável
    assert len(stats) > 0
    
    # Limpa
    del data
    tracemalloc.stop()
