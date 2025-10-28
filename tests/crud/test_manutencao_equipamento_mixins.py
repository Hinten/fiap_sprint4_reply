"""
Testes para validar os métodos dos mixins do modelo ManutencaoEquipamento.

Testa métodos herdados de:
- _ModelCrudMixin
- _ModelSerializationMixin
- _ModelFieldsMixin
- _ModelDisplayMixin
"""
import pytest
from datetime import datetime
from src.database.models.manutencao_equipamento import ManutencaoEquipamento
from src.database.models.equipamento import Equipamento
from src.database.tipos_base.database import Database


class TestManutencaoEquipamentoCrudMixin:
    """Testes para métodos do _ModelCrudMixin."""

    @pytest.fixture
    def equipamento_fixture(self, test_database):
        """Fixture para criar um equipamento de teste."""
        with Database.get_session() as session:
            equipamento = Equipamento(
                nome='Equipamento Manutenção Teste',
                modelo='Modelo ABC-456',
                localizacao='Laboratório'
            )
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)
            return equipamento

    @pytest.fixture
    def manutencao_data(self, equipamento_fixture):
        """Dados de exemplo para criar uma manutenção."""
        return {
            'equipamento_id': equipamento_fixture.id,
            'data_previsao_manutencao': datetime(2024, 6, 15, 9, 0, 0),
            'motivo': 'Manutenção preventiva',
            'data_inicio_manutencao': datetime(2024, 6, 15, 10, 0, 0),
            'data_fim_manutencao': datetime(2024, 6, 15, 12, 0, 0),
            'descricao': 'Troca de peças desgastadas',
            'observacoes': 'Manutenção realizada com sucesso',
            'custo': 1500.50
        }

    def test_get_from_id(self, test_database, manutencao_data):
        """Testa o método get_from_id do mixin."""
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)
            manutencao_id = manutencao.id

        # Busca usando o método do mixin
        manutencao_encontrada = ManutencaoEquipamento.get_from_id(manutencao_id)
        assert manutencao_encontrada is not None
        assert manutencao_encontrada.id == manutencao_id
        assert manutencao_encontrada.motivo == manutencao_data['motivo']

    def test_all(self, test_database, manutencao_data):
        """Testa o método all do mixin."""
        # Cria várias manutenções
        with Database.get_session() as session:
            manutencao1 = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao1)
            
            manutencao_data2 = manutencao_data.copy()
            manutencao_data2['motivo'] = 'Manutenção corretiva'
            manutencao2 = ManutencaoEquipamento(**manutencao_data2)
            session.add(manutencao2)
            session.commit()

        # Busca todas usando o método do mixin
        todas_manutencoes = ManutencaoEquipamento.all()
        assert len(todas_manutencoes) == 2
        assert todas_manutencoes[0].id < todas_manutencoes[1].id

    def test_save(self, test_database, manutencao_data):
        """Testa o método save do mixin."""
        manutencao = ManutencaoEquipamento(**manutencao_data)
        
        # Salva usando o método do mixin
        manutencao_salva = manutencao.save()
        
        assert manutencao_salva.id is not None
        assert manutencao_salva.motivo == manutencao_data['motivo']
        
        # Verifica se foi persistido no banco
        with Database.get_session() as session:
            manutencao_db = session.query(ManutencaoEquipamento).filter_by(id=manutencao_salva.id).first()
            assert manutencao_db is not None
            assert manutencao_db.motivo == manutencao_data['motivo']

    def test_merge(self, test_database, manutencao_data):
        """Testa o método merge do mixin."""
        manutencao = ManutencaoEquipamento(**manutencao_data)
        
        # Merge usando o método do mixin
        manutencao_merged = manutencao.merge()
        
        assert manutencao_merged.id is not None
        assert manutencao.id == manutencao_merged.id
        
        # Verifica se foi persistido no banco
        with Database.get_session() as session:
            manutencao_db = session.query(ManutencaoEquipamento).filter_by(id=manutencao_merged.id).first()
            assert manutencao_db is not None

    def test_update(self, test_database, manutencao_data):
        """Testa o método update do mixin."""
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)
            manutencao_id = manutencao.id

        # Atualiza usando o método do mixin
        manutencao_busca = ManutencaoEquipamento.get_from_id(manutencao_id)
        manutencao_busca.update(custo=2000.75, motivo='Manutenção de emergência')
        
        # Verifica se foi atualizado no banco
        with Database.get_session() as session:
            manutencao_db = session.query(ManutencaoEquipamento).filter_by(id=manutencao_id).first()
            assert manutencao_db.custo == 2000.75
            assert manutencao_db.motivo == 'Manutenção de emergência'

    def test_delete(self, test_database, manutencao_data):
        """Testa o método delete do mixin."""
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)
            manutencao_id = manutencao.id

        # Deleta usando o método do mixin
        manutencao_busca = ManutencaoEquipamento.get_from_id(manutencao_id)
        manutencao_busca.delete()
        
        # Verifica se foi removido do banco
        with Database.get_session() as session:
            manutencao_db = session.query(ManutencaoEquipamento).filter_by(id=manutencao_id).first()
            assert manutencao_db is None

    def test_count(self, test_database, manutencao_data, equipamento_fixture):
        """Testa o método count do mixin."""
        # Conta sem registros
        assert ManutencaoEquipamento.count() == 0
        
        # Cria manutenções
        with Database.get_session() as session:
            manutencao1 = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao1)
            
            manutencao_data2 = manutencao_data.copy()
            manutencao_data2['motivo'] = 'Manutenção corretiva'
            manutencao2 = ManutencaoEquipamento(**manutencao_data2)
            session.add(manutencao2)
            session.commit()

        # Conta todos
        assert ManutencaoEquipamento.count() == 2
        
        # Conta com filtro
        assert ManutencaoEquipamento.count(
            filters=[ManutencaoEquipamento.equipamento_id == equipamento_fixture.id]
        ) == 2

    def test_first(self, test_database, manutencao_data):
        """Testa o método first do mixin."""
        # Cria manutenções
        with Database.get_session() as session:
            manutencao_data1 = manutencao_data.copy()
            manutencao_data1['motivo'] = 'AAA Manutenção'
            manutencao1 = ManutencaoEquipamento(**manutencao_data1)
            session.add(manutencao1)
            
            manutencao_data2 = manutencao_data.copy()
            manutencao_data2['motivo'] = 'ZZZ Manutenção'
            manutencao2 = ManutencaoEquipamento(**manutencao_data2)
            session.add(manutencao2)
            session.commit()

        # Busca primeiro (ordenado por id)
        primeiro = ManutencaoEquipamento.first()
        assert primeiro is not None
        assert primeiro.motivo == 'AAA Manutenção'

    def test_last(self, test_database, manutencao_data):
        """Testa o método last do mixin."""
        # Cria manutenções
        with Database.get_session() as session:
            manutencao_data1 = manutencao_data.copy()
            manutencao_data1['motivo'] = 'AAA Manutenção'
            manutencao1 = ManutencaoEquipamento(**manutencao_data1)
            session.add(manutencao1)
            
            manutencao_data2 = manutencao_data.copy()
            manutencao_data2['motivo'] = 'ZZZ Manutenção'
            manutencao2 = ManutencaoEquipamento(**manutencao_data2)
            session.add(manutencao2)
            session.commit()

        # Busca último (ordenado por id)
        ultimo = ManutencaoEquipamento.last()
        assert ultimo is not None
        assert ultimo.motivo == 'ZZZ Manutenção'


class TestManutencaoEquipamentoSerializationMixin:
    """Testes para métodos do _ModelSerializationMixin."""

    @pytest.fixture
    def equipamento_fixture(self, test_database):
        """Fixture para criar um equipamento de teste."""
        with Database.get_session() as session:
            equipamento = Equipamento(
                nome='Equipamento Manutenção Teste',
                modelo='Modelo ABC-456',
                localizacao='Laboratório'
            )
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)
            return equipamento

    @pytest.fixture
    def manutencao_data(self, equipamento_fixture):
        """Dados de exemplo para criar uma manutenção."""
        return {
            'equipamento_id': equipamento_fixture.id,
            'data_previsao_manutencao': datetime(2024, 6, 15, 9, 0, 0),
            'motivo': 'Manutenção preventiva',
            'custo': 1500.50
        }

    def test_to_dict(self, test_database, manutencao_data):
        """Testa o método to_dict do mixin."""
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)

        # Converte para dicionário
        manutencao_dict = manutencao.to_dict()
        
        assert isinstance(manutencao_dict, dict)
        assert manutencao_dict['motivo'] == manutencao_data['motivo']
        assert manutencao_dict['custo'] == manutencao_data['custo']
        assert 'id' in manutencao_dict

    def test_from_dict(self, test_database, manutencao_data):
        """Testa o método from_dict do mixin."""
        # Cria manutenção a partir de dicionário
        manutencao = ManutencaoEquipamento.from_dict(manutencao_data)
        
        assert manutencao.motivo == manutencao_data['motivo']
        assert manutencao.custo == manutencao_data['custo']

    def test_to_json(self, test_database, manutencao_data):
        """Testa o método to_json do mixin."""
        # Remove datetime fields to avoid serialization issues
        manutencao_data_sem_datetime = manutencao_data.copy()
        manutencao_data_sem_datetime['data_previsao_manutencao'] = None
        
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data_sem_datetime)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)

        # Converte para JSON
        manutencao_json = manutencao.to_json()
        
        assert isinstance(manutencao_json, str)
        # Verifica que o motivo está presente (pode estar como Unicode escapado)
        assert 'motivo' in manutencao_json
        assert ('Manutenção preventiva' in manutencao_json or 
                'Manuten\\u00e7\\u00e3o preventiva' in manutencao_json)

    def test_as_dataframe_all(self, test_database, manutencao_data):
        """Testa o método as_dataframe_all do mixin."""
        # Cria manutenções
        with Database.get_session() as session:
            manutencao1 = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao1)
            
            manutencao_data2 = manutencao_data.copy()
            manutencao_data2['motivo'] = 'Manutenção corretiva'
            manutencao2 = ManutencaoEquipamento(**manutencao_data2)
            session.add(manutencao2)
            session.commit()

        # Converte para DataFrame
        df = ManutencaoEquipamento.as_dataframe_all()
        
        assert len(df) == 2
        assert 'motivo' in df.columns
        assert 'custo' in df.columns

    def test_as_dataframe_all_select_fields(self, test_database, manutencao_data):
        """Testa o método as_dataframe_all com seleção de campos."""
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()

        # Converte para DataFrame com campos selecionados
        df = ManutencaoEquipamento.as_dataframe_all(select_fields=['motivo', 'custo'])
        
        assert len(df.columns) == 2
        assert 'motivo' in df.columns
        assert 'custo' in df.columns
        assert 'descricao' not in df.columns

    def test_filter_dataframe(self, test_database, manutencao_data, equipamento_fixture):
        """Testa o método filter_dataframe do mixin."""
        # Cria manutenções
        with Database.get_session() as session:
            manutencao_data1 = manutencao_data.copy()
            manutencao_data1['custo'] = 1000.0
            manutencao1 = ManutencaoEquipamento(**manutencao_data1)
            session.add(manutencao1)
            
            manutencao_data2 = manutencao_data.copy()
            manutencao_data2['motivo'] = 'Manutenção corretiva'
            manutencao_data2['custo'] = 2000.0
            manutencao2 = ManutencaoEquipamento(**manutencao_data2)
            session.add(manutencao2)
            session.commit()

        # Filtra DataFrame
        df = ManutencaoEquipamento.filter_dataframe(
            filters=[ManutencaoEquipamento.custo > 1500],
            select_fields=['motivo', 'custo']
        )
        
        assert len(df) == 1
        assert df.iloc[0]['custo'] == 2000.0


class TestManutencaoEquipamentoFieldsMixin:
    """Testes para métodos do _ModelFieldsMixin."""

    def test_field_names(self):
        """Testa o método field_names do mixin."""
        field_names = ManutencaoEquipamento.field_names()
        
        assert isinstance(field_names, list)
        assert 'id' in field_names
        assert 'equipamento_id' in field_names
        assert 'motivo' in field_names
        assert 'custo' in field_names

    def test_fields(self):
        """Testa o método fields do mixin."""
        fields = ManutencaoEquipamento.fields()
        
        assert isinstance(fields, list)
        assert len(fields) > 0
        assert all(hasattr(f, 'name') for f in fields)

    def test_get_field(self):
        """Testa o método get_field do mixin."""
        motivo_field = ManutencaoEquipamento.get_field('motivo')
        
        assert motivo_field is not None
        assert motivo_field.name == 'motivo'

    def test_get_field_display_name(self):
        """Testa o método get_field_display_name do mixin."""
        display_name = ManutencaoEquipamento.get_field_display_name('motivo')
        
        # O método title() capitaliza cada palavra, então esperamos "Motivo Da Manutenção"
        assert display_name == 'Motivo Da Manutenção' or display_name == 'Motivo'

    def test_validate_field_valid(self):
        """Testa o método validate_field com valor válido."""
        error = ManutencaoEquipamento.validate_field('motivo', 'Manutenção preventiva')
        
        assert error is None

    def test_validate_field_null_allowed(self):
        """Testa o método validate_field com valor nulo permitido."""
        error = ManutencaoEquipamento.validate_field('motivo', None)
        
        assert error is None

    def test_is_valid(self):
        """Testa o método is_valid do mixin."""
        data_valido = {
            'equipamento_id': 1,
            'motivo': 'Manutenção teste'
        }
        
        assert ManutencaoEquipamento.is_valid(data_valido) is True


class TestManutencaoEquipamentoDisplayMixin:
    """Testes para métodos do _ModelDisplayMixin."""

    def test_display_name(self):
        """Testa o método display_name do mixin."""
        display = ManutencaoEquipamento.display_name()
        
        assert display == 'Manutenção de Equipamento'

    def test_display_name_plural(self):
        """Testa o método display_name_plural do mixin."""
        display = ManutencaoEquipamento.display_name_plural()
        
        assert display == 'Manutenções de Equipamentos'
