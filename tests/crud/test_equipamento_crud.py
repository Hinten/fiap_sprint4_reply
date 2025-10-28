"""
Testes CRUD para o modelo Equipamento.

Testa operações básicas de Create, Read, Update e Delete para a entidade Equipamento.
"""
import pytest
from datetime import datetime
from src.database.models.equipamento import Equipamento
from src.database.tipos_base.database import Database


class TestEquipamentoCRUD:
    """Testes CRUD para Equipamento."""

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

    def test_create_equipamento(self, test_database, equipamento_data):
        """Testa criação de um novo equipamento."""
        with Database.get_session() as session:
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)

            assert equipamento.id is not None
            assert equipamento.nome == equipamento_data['nome']
            assert equipamento.modelo == equipamento_data['modelo']
            assert equipamento.localizacao == equipamento_data['localizacao']

    def test_read_equipamento(self, test_database, equipamento_data):
        """Testa leitura de equipamento do banco."""
        with Database.get_session() as session:
            # Criar equipamento
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)

            # Ler equipamento
            equipamento_lido = session.query(Equipamento).filter_by(id=equipamento.id).first()
            assert equipamento_lido is not None
            assert equipamento_lido.nome == equipamento_data['nome']
            assert equipamento_lido.modelo == equipamento_data['modelo']

    def test_update_equipamento(self, test_database, equipamento_data):
        """Testa atualização de equipamento."""
        with Database.get_session() as session:
            # Criar equipamento
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)

            # Atualizar equipamento
            novo_nome = 'Equipamento Atualizado'
            equipamento.nome = novo_nome
            session.commit()

            # Verificar atualização
            equipamento_atualizado = session.query(Equipamento).filter_by(id=equipamento.id).first()
            assert equipamento_atualizado.nome == novo_nome

    def test_delete_equipamento(self, test_database, equipamento_data):
        """Testa exclusão de equipamento."""
        with Database.get_session() as session:
            # Criar equipamento
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)

            equipamento_id = equipamento.id

            # Excluir equipamento
            session.delete(equipamento)
            session.commit()

            # Verificar exclusão
            equipamento_excluido = session.query(Equipamento).filter_by(id=equipamento_id).first()
            assert equipamento_excluido is None

    def test_equipamento_unique_constraints(self, test_database, equipamento_data):
        """Testa constraints únicos do equipamento."""
        with Database.get_session() as session:
            # Criar primeiro equipamento
            equipamento1 = Equipamento(**equipamento_data)
            session.add(equipamento1)
            session.commit()

            # Tentar criar segundo equipamento com mesmo nome (deve falhar)
            equipamento2 = Equipamento(**equipamento_data)
            session.add(equipamento2)

            with pytest.raises(Exception):  # IntegrityError esperado
                session.commit()

    def test_equipamento_str_method(self, test_database, equipamento_data):
        """Testa mét odo __str__ do equipamento."""
        equipamento = Equipamento(**equipamento_data)
        equipamento.id = 1  # Simular ID para teste
        assert str(equipamento) == f"1 - {equipamento_data['nome']}"

    def test_equipamento_relationships(self, test_database, equipamento_data):
        """Testa relacionamentos do equipamento."""
        with Database.get_session() as session:
            equipamento = Equipamento(**equipamento_data)
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)

            # Verificar que listas de relacionamentos existem
            assert hasattr(equipamento, 'sensores')
            assert hasattr(equipamento, 'manutencoes')
            assert isinstance(equipamento.sensores, list)
            assert isinstance(equipamento.manutencoes, list)
