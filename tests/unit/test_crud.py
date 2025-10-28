"""
Testes para as operações CRUD (_ModelCrudMixin).

Testa todas as operações CRUD disponíveis no mixin:
- get_from_id: Buscar por ID
- all: Listar todos
- save: Criar/salvar
- merge: Merge de dados
- update: Atualizar atributos
- delete: Remover
- count: Contar registros
- first: Primeiro registro
- last: Último registro
"""
import pytest
from sqlalchemy import String, Integer, Sequence
from sqlalchemy.orm import Mapped, mapped_column
from src.database.tipos_base.model import Model
from src.database.tipos_base.database import Database


# Modelo de teste simples
class TestModel(Model):
    """Modelo de teste para operações CRUD."""
    __tablename__ = 'TEST_CRUD_MODEL'
    
    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"),
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
    
    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        info={'label': 'Nome'}
    )
    
    valor: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        info={'label': 'Valor'}
    )


@pytest.fixture
def test_crud_database(tmp_path):
    """Fixture que fornece um banco de dados limpo para testes CRUD."""
    db_path = tmp_path / "test_crud.db"
    Database.init_sqlite(str(db_path))
    Database.create_all_tables(drop_if_exists=True)
    
    yield Database
    
    try:
        Database.drop_all_tables()
    except Exception:
        pass


class TestCRUDOperations:
    """Testes para operações CRUD básicas."""
    
    def test_save_creates_new_record(self, test_crud_database):
        """Testa se save() cria um novo registro."""
        # Cria uma nova instância
        instance = TestModel(nome="Teste 1", valor=100)
        
        # Salva no banco
        saved = instance.save()
        
        # Verifica se foi salvo
        assert saved.id is not None
        assert saved.nome == "Teste 1"
        assert saved.valor == 100
    
    def test_get_from_id_retrieves_record(self, test_crud_database):
        """Testa se get_from_id() busca registro corretamente."""
        # Cria e salva
        instance = TestModel(nome="Teste GetID", valor=200)
        saved = instance.save()
        saved_id = saved.id
        
        # Busca pelo ID
        retrieved = TestModel.get_from_id(saved_id)
        
        assert retrieved is not None
        assert retrieved.id == saved_id
        assert retrieved.nome == "Teste GetID"
        assert retrieved.valor == 200
    
    def test_get_from_id_raises_on_nonexistent(self, test_crud_database):
        """Testa se get_from_id() levanta exceção quando ID não existe."""
        with pytest.raises(Exception):  # NoResultFound
            TestModel.get_from_id(99999)
    
    def test_all_returns_all_records(self, test_crud_database):
        """Testa se all() retorna todos os registros."""
        # Cria vários registros
        TestModel(nome="Registro 1", valor=10).save()
        TestModel(nome="Registro 2", valor=20).save()
        TestModel(nome="Registro 3", valor=30).save()
        
        # Busca todos
        all_records = TestModel.all()
        
        assert len(all_records) == 3
        assert all_records[0].nome == "Registro 1"
        assert all_records[1].nome == "Registro 2"
        assert all_records[2].nome == "Registro 3"
    
    def test_all_returns_ordered_by_id(self, test_crud_database):
        """Testa se all() retorna ordenado por ID."""
        # Cria registros
        r1 = TestModel(nome="Primeiro", valor=1).save()
        r2 = TestModel(nome="Segundo", valor=2).save()
        r3 = TestModel(nome="Terceiro", valor=3).save()
        
        all_records = TestModel.all()
        
        assert all_records[0].id == r1.id
        assert all_records[1].id == r2.id
        assert all_records[2].id == r3.id
    
    def test_update_modifies_attributes(self, test_crud_database):
        """Testa se update() modifica atributos corretamente."""
        # Cria e salva
        instance = TestModel(nome="Original", valor=100).save()
        original_id = instance.id
        
        # Atualiza
        instance.update(nome="Modificado", valor=200)
        
        # Verifica mudanças
        assert instance.nome == "Modificado"
        assert instance.valor == 200
        assert instance.id == original_id
        
        # Verifica persistência
        retrieved = TestModel.get_from_id(original_id)
        assert retrieved.nome == "Modificado"
        assert retrieved.valor == 200
    
    def test_update_ignores_invalid_fields(self, test_crud_database):
        """Testa se update() ignora campos inválidos."""
        instance = TestModel(nome="Teste", valor=100).save()
        
        # Tenta atualizar com campo inválido
        instance.update(nome="Novo", campo_invalido="deve_ignorar")
        
        # Verifica que o campo válido foi atualizado
        assert instance.nome == "Novo"
        # Campo inválido não deve existir
        assert not hasattr(instance, 'campo_invalido')
    
    def test_delete_removes_record(self, test_crud_database):
        """Testa se delete() remove o registro."""
        # Cria e salva
        instance = TestModel(nome="Para Deletar", valor=999).save()
        instance_id = instance.id
        
        # Deleta
        instance.delete()
        
        # Verifica que não existe mais
        with pytest.raises(Exception):  # NoResultFound
            TestModel.get_from_id(instance_id)
    
    def test_merge_creates_or_updates(self, test_crud_database):
        """Testa se merge() cria ou atualiza registro."""
        # Cria instância
        instance = TestModel(nome="Merge Test", valor=50)
        
        # Merge (deve criar)
        merged = instance.merge()
        assert merged.id is not None
        
        # Modifica e merge novamente (deve atualizar)
        merged.nome = "Merge Updated"
        merged.merge()
        
        # Verifica atualização
        retrieved = TestModel.get_from_id(merged.id)
        assert retrieved.nome == "Merge Updated"


class TestCRUDCount:
    """Testes para a operação count()."""
    
    def test_count_returns_total_records(self, test_crud_database):
        """Testa se count() retorna o total de registros."""
        # Cria registros
        TestModel(nome="Count 1", valor=1).save()
        TestModel(nome="Count 2", valor=2).save()
        TestModel(nome="Count 3", valor=3).save()
        
        count = TestModel.count()
        assert count == 3
    
    def test_count_with_filters(self, test_crud_database):
        """Testa se count() funciona com filtros."""
        # Cria registros com valores diferentes
        TestModel(nome="Valor 10", valor=10).save()
        TestModel(nome="Valor 20", valor=20).save()
        TestModel(nome="Valor 10 B", valor=10).save()
        
        # Conta apenas registros com valor=10
        count = TestModel.count(filters=[TestModel.valor == 10])
        assert count == 2
    
    def test_count_empty_table(self, test_crud_database):
        """Testa se count() retorna 0 para tabela vazia."""
        count = TestModel.count()
        assert count == 0


class TestCRUDFirst:
    """Testes para a operação first()."""
    
    def test_first_returns_first_record(self, test_crud_database):
        """Testa se first() retorna o primeiro registro."""
        # Cria registros
        r1 = TestModel(nome="Primeiro", valor=1).save()
        TestModel(nome="Segundo", valor=2).save()
        TestModel(nome="Terceiro", valor=3).save()
        
        first = TestModel.first()
        assert first.id == r1.id
        assert first.nome == "Primeiro"
    
    def test_first_with_filters(self, test_crud_database):
        """Testa se first() funciona com filtros."""
        TestModel(nome="Valor 5", valor=5).save()
        r2 = TestModel(nome="Valor 10", valor=10).save()
        TestModel(nome="Valor 10 B", valor=10).save()
        
        # Primeiro com valor=10
        first = TestModel.first(filters=[TestModel.valor == 10])
        assert first.id == r2.id
        assert first.valor == 10
    
    def test_first_with_order_by(self, test_crud_database):
        """Testa se first() respeita order_by."""
        TestModel(nome="Valor 30", valor=30).save()
        TestModel(nome="Valor 10", valor=10).save()
        r3 = TestModel(nome="Valor 20", valor=20).save()
        
        # Primeiro ordenado por valor ascendente
        first = TestModel.first(order_by=[TestModel.valor.asc()])
        assert first.valor == 10
        
        # Primeiro ordenado por valor descendente
        first = TestModel.first(order_by=[TestModel.valor.desc()])
        assert first.valor == 30
    
    def test_first_empty_table(self, test_crud_database):
        """Testa se first() retorna None para tabela vazia."""
        first = TestModel.first()
        assert first is None
    
    def test_first_no_match_with_filters(self, test_crud_database):
        """Testa se first() retorna None quando não há match."""
        TestModel(nome="Valor 5", valor=5).save()
        
        first = TestModel.first(filters=[TestModel.valor == 999])
        assert first is None


class TestCRUDLast:
    """Testes para a operação last()."""
    
    def test_last_returns_last_record(self, test_crud_database):
        """Testa se last() retorna o último registro."""
        TestModel(nome="Primeiro", valor=1).save()
        TestModel(nome="Segundo", valor=2).save()
        r3 = TestModel(nome="Terceiro", valor=3).save()
        
        last = TestModel.last()
        assert last.id == r3.id
        assert last.nome == "Terceiro"
    
    def test_last_with_filters(self, test_crud_database):
        """Testa se last() funciona com filtros."""
        TestModel(nome="Valor 5", valor=5).save()
        TestModel(nome="Valor 10", valor=10).save()
        r3 = TestModel(nome="Valor 10 B", valor=10).save()
        
        # Último com valor=10
        last = TestModel.last(filters=[TestModel.valor == 10])
        assert last.id == r3.id
        assert last.valor == 10
    
    def test_last_with_order_by(self, test_crud_database):
        """Testa se last() respeita order_by."""
        TestModel(nome="Valor 30", valor=30).save()
        TestModel(nome="Valor 10", valor=10).save()
        TestModel(nome="Valor 20", valor=20).save()
        
        # Último ordenado por valor ascendente (deve ser 30)
        last = TestModel.last(order_by=[TestModel.valor.asc()])
        assert last.valor == 30
        
        # Último ordenado por valor descendente (deve ser 10)
        last = TestModel.last(order_by=[TestModel.valor.desc()])
        assert last.valor == 10
    
    def test_last_empty_table(self, test_crud_database):
        """Testa se last() retorna None para tabela vazia."""
        last = TestModel.last()
        assert last is None
    
    def test_last_no_match_with_filters(self, test_crud_database):
        """Testa se last() retorna None quando não há match."""
        TestModel(nome="Valor 5", valor=5).save()
        
        last = TestModel.last(filters=[TestModel.valor == 999])
        assert last is None


class TestCRUDEdgeCases:
    """Testes para casos extremos e edge cases."""
    
    def test_save_multiple_times_same_instance(self, test_crud_database):
        """Testa salvar a mesma instância múltiplas vezes."""
        instance = TestModel(nome="Multi Save", valor=100)
        
        # Primeira salvada
        saved1 = instance.save()
        id1 = saved1.id
        
        # Modifica e salva novamente
        instance.nome = "Modified"
        saved2 = instance.save()
        
        # Deve manter o mesmo ID
        assert saved2.id == id1
        
        # Verifica que foi atualizado
        retrieved = TestModel.get_from_id(id1)
        assert retrieved.nome == "Modified"
    
    def test_null_value_handling(self, test_crud_database):
        """Testa tratamento de valores nulos."""
        # Cria com valor nulo
        instance = TestModel(nome="Null Test", valor=None)
        saved = instance.save()
        
        assert saved.valor is None
        
        # Busca e verifica
        retrieved = TestModel.get_from_id(saved.id)
        assert retrieved.valor is None
    
    def test_update_to_null(self, test_crud_database):
        """Testa atualizar campo para null."""
        instance = TestModel(nome="Has Value", valor=999).save()
        
        # Atualiza para None
        instance.update(valor=None)
        
        assert instance.valor is None
        
        # Verifica persistência
        retrieved = TestModel.get_from_id(instance.id)
        assert retrieved.valor is None
    
    def test_empty_update(self, test_crud_database):
        """Testa update() sem parâmetros."""
        instance = TestModel(nome="No Change", valor=50).save()
        original_nome = instance.nome
        original_valor = instance.valor
        
        # Update sem parâmetros
        instance.update()
        
        # Nada deve mudar
        assert instance.nome == original_nome
        assert instance.valor == original_valor
    
    def test_count_with_empty_filters(self, test_crud_database):
        """Testa count() com lista de filtros vazia."""
        TestModel(nome="Test 1", valor=1).save()
        TestModel(nome="Test 2", valor=2).save()
        
        # Count com lista vazia deve retornar todos
        count = TestModel.count(filters=[])
        assert count == 2
    
    def test_concurrent_saves(self, test_crud_database):
        """Testa múltiplas instâncias salvas em sequência."""
        instances = [
            TestModel(nome=f"Concurrent {i}", valor=i)
            for i in range(10)
        ]
        
        # Salva todas
        saved = [inst.save() for inst in instances]
        
        # Verifica que todas têm IDs únicos
        ids = [s.id for s in saved]
        assert len(ids) == len(set(ids))  # Sem duplicatas
        
        # Verifica total
        assert TestModel.count() == 10


class TestCRUDBugFixes:
    """
    Testes para bugs potenciais identificados no código CRUD.
    """
    
    def test_update_without_session_add(self, test_crud_database):
        """
        BUG POTENCIAL: update() não adiciona instância à sessão.
        
        O método update() em crud.py (linha 75-77) chama session.commit()
        mas não adiciona a instância à sessão primeiro.
        Isso pode causar problemas se a instância não estiver anexada.
        """
        # Cria e salva
        instance = TestModel(nome="Original", valor=100).save()
        instance_id = instance.id
        
        # Busca novamente para ter uma instância "desanexada"
        retrieved = TestModel.get_from_id(instance_id)
        
        # Tenta atualizar
        retrieved.nome = "Modificado Manual"
        retrieved.update(valor=200)
        
        # Verifica se atualizou
        final = TestModel.get_from_id(instance_id)
        assert final.valor == 200
        # Este assert pode falhar se update() não funcionar corretamente
        # com instâncias desanexadas
    
    def test_delete_detached_instance(self, test_crud_database):
        """
        BUG POTENCIAL: delete() com instância desanexada.
        
        Similar ao update(), delete() pode ter problemas com instâncias
        que não estão anexadas à sessão.
        """
        # Cria e salva
        instance = TestModel(nome="To Delete", valor=999).save()
        instance_id = instance.id
        
        # Busca novamente
        retrieved = TestModel.get_from_id(instance_id)
        
        # Tenta deletar
        retrieved.delete()
        
        # Verifica que foi deletado
        with pytest.raises(Exception):
            TestModel.get_from_id(instance_id)
    
    def test_session_cleanup_after_operations(self, test_crud_database):
        """
        Verifica se sessões são limpas corretamente após operações.
        Memory leak potencial se sessões não forem fechadas.
        """
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Executa muitas operações CRUD
        for i in range(100):
            instance = TestModel(nome=f"Memory Test {i}", valor=i).save()
            TestModel.get_from_id(instance.id)
            instance.update(valor=i+1)
            if i % 2 == 0:  # Deleta metade
                instance.delete()
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Crescimento deve ser mínimo (< 5MB)
        assert memory_growth < 5 * 1024 * 1024, \
            f"Possível memory leak: {memory_growth / 1024 / 1024:.2f}MB"
