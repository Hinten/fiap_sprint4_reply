"""
Testes CRUD para o modelo ManutencaoEquipamento.

Testa operações básicas de Create, Read, Update e Delete para a entidade ManutencaoEquipamento.
"""
import pytest
from datetime import datetime
from src.database.models.manutencao_equipamento import ManutencaoEquipamento
from src.database.models.equipamento import Equipamento
from src.database.tipos_base.database import Database
from sqlalchemy.orm import joinedload


class TestManutencaoEquipamentoCRUD:
    """Testes CRUD para ManutencaoEquipamento."""

    @pytest.fixture
    def equipamento_fixture(self, test_database):
        """Fixture para criar um equipamento de teste."""
        with Database.get_session() as session:
            equipamento = Equipamento(
                nome='Equipamento para Manutenção',
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

    def test_create_manutencao_equipamento(self, test_database, manutencao_data):
        """Testa criação de uma nova manutenção."""
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)

            assert manutencao.id is not None
            assert manutencao.motivo == manutencao_data['motivo']
            assert manutencao.custo == manutencao_data['custo']
            assert manutencao.equipamento_id == manutencao_data['equipamento_id']

    def test_read_manutencao_equipamento(self, test_database, manutencao_data):
        """Testa leitura de manutenção do banco."""
        with Database.get_session() as session:
            # Criar manutenção
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)

            # Ler manutenção
            manutencao_lida = session.query(ManutencaoEquipamento).filter_by(id=manutencao.id).first()
            assert manutencao_lida is not None
            assert manutencao_lida.motivo == manutencao_data['motivo']
            assert manutencao_lida.custo == manutencao_data['custo']

    def test_update_manutencao_equipamento(self, test_database, manutencao_data):
        """Testa atualização de manutenção."""
        with Database.get_session() as session:
            # Criar manutenção
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)

            # Atualizar manutenção
            novo_custo = 2000.75
            manutencao.custo = novo_custo
            session.commit()

            # Verificar atualização
            manutencao_atualizada = session.query(ManutencaoEquipamento).filter_by(id=manutencao.id).first()
            assert manutencao_atualizada.custo == novo_custo

    def test_delete_manutencao_equipamento(self, test_database, manutencao_data):
        """Testa exclusão de manutenção."""
        with Database.get_session() as session:
            # Criar manutenção
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)

            manutencao_id = manutencao.id

            # Excluir manutenção
            session.delete(manutencao)
            session.commit()

            # Verificar exclusão
            manutencao_excluida = session.query(ManutencaoEquipamento).filter_by(id=manutencao_id).first()
            assert manutencao_excluida is None

    def test_manutencao_equipamento_relationship(self, test_database, equipamento_fixture, manutencao_data):
        """Testa relacionamento entre manutenção e equipamento."""
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)

            # Recarregar objetos com relacionamentos
            manutencao = session.query(ManutencaoEquipamento).options(
                joinedload(ManutencaoEquipamento.equipamento)
            ).filter_by(id=manutencao.id).first()

            equipamento_fixture = session.query(Equipamento).options(
                joinedload(Equipamento.manutencoes)
            ).filter_by(id=equipamento_fixture.id).first()

            # Verificar relacionamento bidirecional
            assert manutencao.equipamento is not None
            assert manutencao.equipamento.id == equipamento_fixture.id
            assert manutencao in equipamento_fixture.manutencoes

    def test_manutencao_equipamento_str_method(self, test_database, equipamento_fixture, manutencao_data):
        """Testa mét odo __str__ da manutenção."""
        with Database.get_session() as session:
            manutencao = ManutencaoEquipamento(**manutencao_data)
            session.add(manutencao)
            session.commit()
            session.refresh(manutencao)
            
            # Recarregar equipamento para ter acesso aos dados
            session.refresh(equipamento_fixture)
            
            expected = f"{manutencao.id} - {equipamento_fixture.nome} - {manutencao_data['data_inicio_manutencao']} a {manutencao_data['data_fim_manutencao']}"
            assert str(manutencao) == expected

    def test_manutencao_equipamento_foreign_key_constraint(self, test_database):
        """Testa constraint de chave estrangeira."""
        with Database.get_session() as session:
            # Habilitar foreign keys no SQLite
            session.execute("PRAGMA foreign_keys = ON")
            
            # Tentar criar manutenção com equipamento_id inexistente
            manutencao = ManutencaoEquipamento(
                equipamento_id=99999,  # ID inexistente
                motivo='Teste constraint'
            )
            session.add(manutencao)

            with pytest.raises(Exception):  # IntegrityError esperado
                session.commit()
