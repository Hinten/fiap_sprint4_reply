"""
Testes CRUD para o modelo Empresa.

Testa operações básicas de Create, Read, Update e Delete para a entidade Empresa.
"""
import pytest
from src.database.models.empresa import Empresa, SiglaEstadoEnum
from src.database.tipos_base.database import Database


class TestEmpresaCRUD:
    """Testes CRUD para Empresa."""

    @pytest.fixture
    def empresa_data(self):
        """Dados de exemplo para criar uma empresa."""
        return {
            'nome': 'Empresa Teste Ltda',
            'cnpj': '12345678000123',
            'logradouro': 'Rua das Flores',
            'numero': '123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': SiglaEstadoEnum.SP,
            'cep': '01234567'
        }

    def test_create_empresa(self, test_database, empresa_data):
        """Testa criação de uma nova empresa."""
        with Database.get_session() as session:
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)

            assert empresa.id is not None
            assert empresa.nome == empresa_data['nome']
            assert empresa.cnpj == empresa_data['cnpj']
            assert empresa.estado == empresa_data['estado']

    def test_read_empresa(self, test_database, empresa_data):
        """Testa leitura de empresa do banco."""
        with Database.get_session() as session:
            # Criar empresa
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)

            # Ler empresa
            empresa_lida = session.query(Empresa).filter_by(id=empresa.id).first()
            assert empresa_lida is not None
            assert empresa_lida.nome == empresa_data['nome']
            assert empresa_lida.cnpj == empresa_data['cnpj']

    def test_update_empresa(self, test_database, empresa_data):
        """Testa atualização de empresa."""
        with Database.get_session() as session:
            # Criar empresa
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)

            # Atualizar empresa
            novo_nome = 'Empresa Atualizada Ltda'
            empresa.nome = novo_nome
            session.commit()

            # Verificar atualização
            empresa_atualizada = session.query(Empresa).filter_by(id=empresa.id).first()
            assert empresa_atualizada.nome == novo_nome

    def test_delete_empresa(self, test_database, empresa_data):
        """Testa exclusão de empresa."""
        with Database.get_session() as session:
            # Criar empresa
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)

            empresa_id = empresa.id

            # Excluir empresa
            session.delete(empresa)
            session.commit()

            # Verificar exclusão
            empresa_excluida = session.query(Empresa).filter_by(id=empresa_id).first()
            assert empresa_excluida is None

    def test_empresa_unique_constraints(self, test_database, empresa_data):
        """Testa constraints únicos da empresa."""
        with Database.get_session() as session:
            # Criar primeira empresa
            empresa1 = Empresa(**empresa_data)
            session.add(empresa1)
            session.commit()

            # Tentar criar segunda empresa com mesmo nome (deve falhar)
            empresa2 = Empresa(**empresa_data)
            session.add(empresa2)

            with pytest.raises(Exception):  # IntegrityError esperado
                session.commit()

    def test_empresa_str_method(self, test_database, empresa_data):
        """Testa mét odo __str__ da empresa."""
        with Database.get_session() as session:
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)
            
            # Agora o objeto tem ID válido
            assert str(empresa) == f"{empresa.id} - {empresa_data['nome']}"