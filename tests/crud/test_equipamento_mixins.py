"""
Testes para validar os métodos dos mixins do modelo Equipamento.

Testa métodos herdados de:
- _ModelCrudMixin
- _ModelSerializationMixin
- _ModelFieldsMixin
- _ModelDisplayMixin
"""
import pytest
from datetime import datetime
from src.database.models.equipamento import Equipamento
from src.database.tipos_base.database import Database


class TestEquipamentoCrudMixin:
    """Testes para métodos do _ModelCrudMixin."""

    @pytest.fixture
    def equipamento_data(self):
        """Dados de exemplo para criar um equipamento."""
        return {
            'nome': 'Equipamento Teste',
            'modelo': 'Modelo XYZ-123',
            'localizacao': 'Sala de Servidores',
            'descricao': 'Equipamento de teste para validação',
            'observacoes': 'Observações de teste',
            'data_instalacao': datetime(2023, 1, 15, 10, 30, 0)
        }

    def test_get_from_id(self, test_database, equipamento_data):
        """Testa o método get_from_id do mixin."""
        with Database.get_session() as session:
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)
            equipamento_id = equipamento.id

        # Busca usando o método do mixin
        equipamento_encontrado = Equipamento.get_from_id(equipamento_id)
        assert equipamento_encontrado is not None
        assert equipamento_encontrado.id == equipamento_id
        assert equipamento_encontrado.nome == equipamento_data['nome']

    def test_all(self, test_database, equipamento_data):
        """Testa o método all do mixin."""
        # Cria vários equipamentos
        with Database.get_session() as session:
            equipamento1 = Equipamento(**equipamento_data)
            session.add(equipamento1)
            
            equipamento_data2 = equipamento_data.copy()
            equipamento_data2['nome'] = 'Equipamento Dois'
            equipamento2 = Equipamento(**equipamento_data2)
            session.add(equipamento2)
            session.commit()

        # Busca todos usando o método do mixin
        todos_equipamentos = Equipamento.all()
        assert len(todos_equipamentos) == 2
        assert todos_equipamentos[0].id < todos_equipamentos[1].id  # Verifica ordenação por id

    def test_save(self, test_database, equipamento_data):
        """Testa o método save do mixin."""
        equipamento = Equipamento(**equipamento_data)
        
        # Salva usando o método do mixin
        equipamento_salvo = equipamento.save()
        
        assert equipamento_salvo.id is not None
        assert equipamento_salvo.nome == equipamento_data['nome']
        
        # Verifica se foi persistido no banco
        with Database.get_session() as session:
            equipamento_db = session.query(Equipamento).filter_by(id=equipamento_salvo.id).first()
            assert equipamento_db is not None
            assert equipamento_db.nome == equipamento_data['nome']

    def test_merge(self, test_database, equipamento_data):
        """Testa o método merge do mixin."""
        equipamento = Equipamento(**equipamento_data)
        
        # Merge usando o método do mixin
        equipamento_merged = equipamento.merge()
        
        assert equipamento_merged.id is not None
        assert equipamento.id == equipamento_merged.id
        
        # Verifica se foi persistido no banco
        with Database.get_session() as session:
            equipamento_db = session.query(Equipamento).filter_by(id=equipamento_merged.id).first()
            assert equipamento_db is not None

    def test_update(self, test_database, equipamento_data):
        """Testa o método update do mixin."""
        with Database.get_session() as session:
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)
            equipamento_id = equipamento.id

        # Atualiza usando o método do mixin
        equipamento_busca = Equipamento.get_from_id(equipamento_id)
        equipamento_busca.update(nome='Equipamento Atualizado', localizacao='Nova Sala')
        
        # Verifica se foi atualizado no banco
        with Database.get_session() as session:
            equipamento_db = session.query(Equipamento).filter_by(id=equipamento_id).first()
            assert equipamento_db.nome == 'Equipamento Atualizado'
            assert equipamento_db.localizacao == 'Nova Sala'
            assert equipamento_db.modelo == equipamento_data['modelo']

    def test_delete(self, test_database, equipamento_data):
        """Testa o método delete do mixin."""
        with Database.get_session() as session:
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)
            equipamento_id = equipamento.id

        # Deleta usando o método do mixin
        equipamento_busca = Equipamento.get_from_id(equipamento_id)
        equipamento_busca.delete()
        
        # Verifica se foi removido do banco
        with Database.get_session() as session:
            equipamento_db = session.query(Equipamento).filter_by(id=equipamento_id).first()
            assert equipamento_db is None

    def test_count(self, test_database, equipamento_data):
        """Testa o método count do mixin."""
        # Conta sem registros
        assert Equipamento.count() == 0
        
        # Cria equipamentos
        with Database.get_session() as session:
            equipamento1 = Equipamento(**equipamento_data)
            session.add(equipamento1)
            
            equipamento_data2 = equipamento_data.copy()
            equipamento_data2['nome'] = 'Equipamento Dois'
            equipamento_data2['localizacao'] = 'Sala 2'
            equipamento2 = Equipamento(**equipamento_data2)
            session.add(equipamento2)
            session.commit()

        # Conta todos
        assert Equipamento.count() == 2
        
        # Conta com filtro
        assert Equipamento.count(filters=[Equipamento.localizacao == 'Sala de Servidores']) == 1

    def test_first(self, test_database, equipamento_data):
        """Testa o método first do mixin."""
        # Cria equipamentos
        with Database.get_session() as session:
            equipamento_data1 = equipamento_data.copy()
            equipamento_data1['nome'] = 'AAA Equipamento'
            equipamento1 = Equipamento(**equipamento_data1)
            session.add(equipamento1)
            
            equipamento_data2 = equipamento_data.copy()
            equipamento_data2['nome'] = 'ZZZ Equipamento'
            equipamento2 = Equipamento(**equipamento_data2)
            session.add(equipamento2)
            session.commit()

        # Busca primeiro (ordenado por id)
        primeiro = Equipamento.first()
        assert primeiro is not None
        assert primeiro.nome == 'AAA Equipamento'

    def test_last(self, test_database, equipamento_data):
        """Testa o método last do mixin."""
        # Cria equipamentos
        with Database.get_session() as session:
            equipamento_data1 = equipamento_data.copy()
            equipamento_data1['nome'] = 'AAA Equipamento'
            equipamento1 = Equipamento(**equipamento_data1)
            session.add(equipamento1)
            
            equipamento_data2 = equipamento_data.copy()
            equipamento_data2['nome'] = 'ZZZ Equipamento'
            equipamento2 = Equipamento(**equipamento_data2)
            session.add(equipamento2)
            session.commit()

        # Busca último (ordenado por id)
        ultimo = Equipamento.last()
        assert ultimo is not None
        assert ultimo.nome == 'ZZZ Equipamento'


class TestEquipamentoSerializationMixin:
    """Testes para métodos do _ModelSerializationMixin."""

    @pytest.fixture
    def equipamento_data(self):
        """Dados de exemplo para criar um equipamento."""
        return {
            'nome': 'Equipamento Teste',
            'modelo': 'Modelo XYZ-123',
            'localizacao': 'Sala de Servidores',
            'descricao': 'Equipamento de teste',
            'data_instalacao': datetime(2023, 1, 15, 10, 30, 0)
        }

    def test_to_dict(self, test_database, equipamento_data):
        """Testa o método to_dict do mixin."""
        with Database.get_session() as session:
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)

        # Converte para dicionário
        equipamento_dict = equipamento.to_dict()
        
        assert isinstance(equipamento_dict, dict)
        assert equipamento_dict['nome'] == equipamento_data['nome']
        assert equipamento_dict['modelo'] == equipamento_data['modelo']
        assert 'id' in equipamento_dict

    def test_from_dict(self, test_database, equipamento_data):
        """Testa o método from_dict do mixin."""
        # Cria equipamento a partir de dicionário
        equipamento = Equipamento.from_dict(equipamento_data)
        
        assert equipamento.nome == equipamento_data['nome']
        assert equipamento.modelo == equipamento_data['modelo']

    def test_to_json(self, test_database, equipamento_data):
        """Testa o método to_json do mixin."""
        with Database.get_session() as session:
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)

        # Converte para JSON
        equipamento_json = equipamento.to_json()
        
        assert isinstance(equipamento_json, str)
        assert equipamento_data['nome'] in equipamento_json

    def test_as_dataframe_all(self, test_database, equipamento_data):
        """Testa o método as_dataframe_all do mixin."""
        # Cria equipamentos
        with Database.get_session() as session:
            equipamento1 = Equipamento(**equipamento_data)
            session.add(equipamento1)
            
            equipamento_data2 = equipamento_data.copy()
            equipamento_data2['nome'] = 'Equipamento Dois'
            equipamento2 = Equipamento(**equipamento_data2)
            session.add(equipamento2)
            session.commit()

        # Converte para DataFrame
        df = Equipamento.as_dataframe_all()
        
        assert len(df) == 2
        assert 'nome' in df.columns
        assert 'modelo' in df.columns

    def test_filter_dataframe(self, test_database, equipamento_data):
        """Testa o método filter_dataframe do mixin."""
        # Cria equipamentos
        with Database.get_session() as session:
            equipamento_data1 = equipamento_data.copy()
            equipamento_data1['localizacao'] = 'Sala 1'
            equipamento1 = Equipamento(**equipamento_data1)
            session.add(equipamento1)
            
            equipamento_data2 = equipamento_data.copy()
            equipamento_data2['nome'] = 'Equipamento Dois'
            equipamento_data2['localizacao'] = 'Sala 2'
            equipamento2 = Equipamento(**equipamento_data2)
            session.add(equipamento2)
            session.commit()

        # Filtra DataFrame
        df = Equipamento.filter_dataframe(
            filters=[Equipamento.localizacao == 'Sala 1'],
            select_fields=['nome', 'localizacao']
        )
        
        assert len(df) == 1
        assert df.iloc[0]['nome'] == equipamento_data['nome']


class TestEquipamentoFieldsMixin:
    """Testes para métodos do _ModelFieldsMixin."""

    def test_field_names(self):
        """Testa o método field_names do mixin."""
        field_names = Equipamento.field_names()
        
        assert isinstance(field_names, list)
        assert 'id' in field_names
        assert 'nome' in field_names
        assert 'modelo' in field_names
        assert 'localizacao' in field_names

    def test_fields(self):
        """Testa o método fields do mixin."""
        fields = Equipamento.fields()
        
        assert isinstance(fields, list)
        assert len(fields) > 0
        assert all(hasattr(f, 'name') for f in fields)

    def test_get_field(self):
        """Testa o método get_field do mixin."""
        nome_field = Equipamento.get_field('nome')
        
        assert nome_field is not None
        assert nome_field.name == 'nome'

    def test_get_field_display_name(self):
        """Testa o método get_field_display_name do mixin."""
        display_name = Equipamento.get_field_display_name('nome')
        
        assert display_name == 'Nome'

    def test_validate_field_valid(self):
        """Testa o método validate_field com valor válido."""
        error = Equipamento.validate_field('nome', 'Equipamento Teste')
        
        assert error is None

    def test_validate_field_null_not_allowed(self):
        """Testa o método validate_field com valor nulo não permitido."""
        error = Equipamento.validate_field('nome', None)
        
        assert error is not None
        assert 'não pode ser nulo' in error.lower()

    def test_is_valid(self):
        """Testa o método is_valid do mixin."""
        data_valido = {
            'nome': 'Equipamento Teste'
        }
        
        assert Equipamento.is_valid(data_valido) is True


class TestEquipamentoDisplayMixin:
    """Testes para métodos do _ModelDisplayMixin."""

    def test_display_name(self):
        """Testa o método display_name do mixin."""
        display = Equipamento.display_name()
        
        assert display == 'Equipamento'

    def test_display_name_plural(self):
        """Testa o método display_name_plural do mixin."""
        display = Equipamento.display_name_plural()
        
        assert display == 'Equipamentos'
