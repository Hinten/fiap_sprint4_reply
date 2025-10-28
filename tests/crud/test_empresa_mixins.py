"""
Testes para validar os métodos dos mixins do modelo Empresa.

Testa métodos herdados de:
- _ModelCrudMixin
- _ModelSerializationMixin
- _ModelFieldsMixin
- _ModelDisplayMixin
"""
import pytest
from datetime import datetime
from src.database.models.empresa import Empresa, SiglaEstadoEnum
from src.database.tipos_base.database import Database


class TestEmpresaCrudMixin:
    """Testes para métodos do _ModelCrudMixin."""

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

    def test_get_from_id(self, test_database, empresa_data):
        """Testa o método get_from_id do mixin."""
        with Database.get_session() as session:
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)
            empresa_id = empresa.id

        # Busca usando o método do mixin
        empresa_encontrada = Empresa.get_from_id(empresa_id)
        assert empresa_encontrada is not None
        assert empresa_encontrada.id == empresa_id
        assert empresa_encontrada.nome == empresa_data['nome']

    def test_all(self, test_database, empresa_data):
        """Testa o método all do mixin."""
        # Cria várias empresas
        with Database.get_session() as session:
            empresa1 = Empresa(**empresa_data)
            session.add(empresa1)
            
            empresa_data2 = empresa_data.copy()
            empresa_data2['nome'] = 'Empresa Dois Ltda'
            empresa_data2['cnpj'] = '98765432000198'
            empresa2 = Empresa(**empresa_data2)
            session.add(empresa2)
            session.commit()

        # Busca todas usando o método do mixin
        todas_empresas = Empresa.all()
        assert len(todas_empresas) == 2
        assert todas_empresas[0].id < todas_empresas[1].id  # Verifica ordenação por id

    def test_save(self, test_database, empresa_data):
        """Testa o método save do mixin."""
        empresa = Empresa(**empresa_data)
        
        # Salva usando o método do mixin
        empresa_salva = empresa.save()
        
        assert empresa_salva.id is not None
        assert empresa_salva.nome == empresa_data['nome']
        
        # Verifica se foi persistido no banco
        with Database.get_session() as session:
            empresa_db = session.query(Empresa).filter_by(id=empresa_salva.id).first()
            assert empresa_db is not None
            assert empresa_db.nome == empresa_data['nome']

    def test_merge(self, test_database, empresa_data):
        """Testa o método merge do mixin."""
        empresa = Empresa(**empresa_data)
        
        # Merge usando o método do mixin
        empresa_merged = empresa.merge()
        
        assert empresa_merged.id is not None
        assert empresa.id == empresa_merged.id  # Verifica se o ID foi atualizado na instância original
        
        # Verifica se foi persistido no banco
        with Database.get_session() as session:
            empresa_db = session.query(Empresa).filter_by(id=empresa_merged.id).first()
            assert empresa_db is not None

    def test_update(self, test_database, empresa_data):
        """Testa o método update do mixin."""
        with Database.get_session() as session:
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)
            empresa_id = empresa.id

        # Atualiza usando o método do mixin
        empresa_busca = Empresa.get_from_id(empresa_id)
        empresa_busca.update(nome='Empresa Atualizada Ltda', cidade='Rio de Janeiro')
        
        # Verifica se foi atualizado no banco
        with Database.get_session() as session:
            empresa_db = session.query(Empresa).filter_by(id=empresa_id).first()
            assert empresa_db.nome == 'Empresa Atualizada Ltda'
            assert empresa_db.cidade == 'Rio de Janeiro'
            assert empresa_db.cnpj == empresa_data['cnpj']  # Verifica que outros campos não mudaram

    def test_delete(self, test_database, empresa_data):
        """Testa o método delete do mixin."""
        with Database.get_session() as session:
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)
            empresa_id = empresa.id

        # Deleta usando o método do mixin
        empresa_busca = Empresa.get_from_id(empresa_id)
        empresa_busca.delete()
        
        # Verifica se foi removido do banco
        with Database.get_session() as session:
            empresa_db = session.query(Empresa).filter_by(id=empresa_id).first()
            assert empresa_db is None

    def test_count(self, test_database, empresa_data):
        """Testa o método count do mixin."""
        # Conta sem registros
        assert Empresa.count() == 0
        
        # Cria empresas
        with Database.get_session() as session:
            empresa1 = Empresa(**empresa_data)
            session.add(empresa1)
            
            empresa_data2 = empresa_data.copy()
            empresa_data2['nome'] = 'Empresa Dois Ltda'
            empresa_data2['cnpj'] = '98765432000198'
            empresa_data2['estado'] = SiglaEstadoEnum.RJ
            empresa2 = Empresa(**empresa_data2)
            session.add(empresa2)
            session.commit()

        # Conta todos
        assert Empresa.count() == 2
        
        # Conta com filtro
        assert Empresa.count(filters=[Empresa.estado == SiglaEstadoEnum.SP]) == 1
        assert Empresa.count(filters=[Empresa.estado == SiglaEstadoEnum.RJ]) == 1

    def test_first(self, test_database, empresa_data):
        """Testa o método first do mixin."""
        # Cria empresas
        with Database.get_session() as session:
            empresa_data1 = empresa_data.copy()
            empresa_data1['nome'] = 'AAA Empresa'
            empresa1 = Empresa(**empresa_data1)
            session.add(empresa1)
            
            empresa_data2 = empresa_data.copy()
            empresa_data2['nome'] = 'ZZZ Empresa'
            empresa_data2['cnpj'] = '98765432000198'
            empresa2 = Empresa(**empresa_data2)
            session.add(empresa2)
            session.commit()

        # Busca primeiro (ordenado por id)
        primeiro = Empresa.first()
        assert primeiro is not None
        assert primeiro.nome == 'AAA Empresa'
        
        # Busca primeiro com filtro
        primeiro_filtrado = Empresa.first(filters=[Empresa.nome == 'ZZZ Empresa'])
        assert primeiro_filtrado is not None
        assert primeiro_filtrado.nome == 'ZZZ Empresa'

    def test_last(self, test_database, empresa_data):
        """Testa o método last do mixin."""
        # Cria empresas
        with Database.get_session() as session:
            empresa_data1 = empresa_data.copy()
            empresa_data1['nome'] = 'AAA Empresa'
            empresa1 = Empresa(**empresa_data1)
            session.add(empresa1)
            
            empresa_data2 = empresa_data.copy()
            empresa_data2['nome'] = 'ZZZ Empresa'
            empresa_data2['cnpj'] = '98765432000198'
            empresa2 = Empresa(**empresa_data2)
            session.add(empresa2)
            session.commit()

        # Busca último (ordenado por id)
        ultimo = Empresa.last()
        assert ultimo is not None
        assert ultimo.nome == 'ZZZ Empresa'


class TestEmpresaSerializationMixin:
    """Testes para métodos do _ModelSerializationMixin."""

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

    def test_to_dict(self, test_database, empresa_data):
        """Testa o método to_dict do mixin."""
        with Database.get_session() as session:
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)

        # Converte para dicionário
        empresa_dict = empresa.to_dict()
        
        assert isinstance(empresa_dict, dict)
        assert empresa_dict['nome'] == empresa_data['nome']
        assert empresa_dict['cnpj'] == empresa_data['cnpj']
        assert empresa_dict['estado'] == empresa_data['estado']
        assert 'id' in empresa_dict

    def test_from_dict(self, test_database, empresa_data):
        """Testa o método from_dict do mixin."""
        # Cria empresa a partir de dicionário
        empresa = Empresa.from_dict(empresa_data)
        
        assert empresa.nome == empresa_data['nome']
        assert empresa.cnpj == empresa_data['cnpj']
        assert empresa.estado == empresa_data['estado']

    def test_to_json(self, test_database, empresa_data):
        """Testa o método to_json do mixin."""
        with Database.get_session() as session:
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()
            session.refresh(empresa)

        # Converte para JSON
        empresa_json = empresa.to_json()
        
        assert isinstance(empresa_json, str)
        assert empresa_data['nome'] in empresa_json
        assert empresa_data['cnpj'] in empresa_json

    def test_as_dataframe_all(self, test_database, empresa_data):
        """Testa o método as_dataframe_all do mixin."""
        # Cria empresas
        with Database.get_session() as session:
            empresa1 = Empresa(**empresa_data)
            session.add(empresa1)
            
            empresa_data2 = empresa_data.copy()
            empresa_data2['nome'] = 'Empresa Dois Ltda'
            empresa_data2['cnpj'] = '98765432000198'
            empresa2 = Empresa(**empresa_data2)
            session.add(empresa2)
            session.commit()

        # Converte para DataFrame
        df = Empresa.as_dataframe_all()
        
        assert len(df) == 2
        assert 'nome' in df.columns
        assert 'cnpj' in df.columns
        assert empresa_data['nome'] in df['nome'].values

    def test_as_dataframe_all_select_fields(self, test_database, empresa_data):
        """Testa o método as_dataframe_all com seleção de campos."""
        with Database.get_session() as session:
            empresa = Empresa(**empresa_data)
            session.add(empresa)
            session.commit()

        # Converte para DataFrame com campos selecionados
        df = Empresa.as_dataframe_all(select_fields=['nome', 'cnpj'])
        
        assert len(df.columns) == 2
        assert 'nome' in df.columns
        assert 'cnpj' in df.columns
        assert 'cidade' not in df.columns

    def test_filter_dataframe(self, test_database, empresa_data):
        """Testa o método filter_dataframe do mixin."""
        # Cria empresas
        with Database.get_session() as session:
            empresa_data1 = empresa_data.copy()
            empresa_data1['estado'] = SiglaEstadoEnum.SP
            empresa1 = Empresa(**empresa_data1)
            session.add(empresa1)
            
            empresa_data2 = empresa_data.copy()
            empresa_data2['nome'] = 'Empresa Dois Ltda'
            empresa_data2['cnpj'] = '98765432000198'
            empresa_data2['estado'] = SiglaEstadoEnum.RJ
            empresa2 = Empresa(**empresa_data2)
            session.add(empresa2)
            session.commit()

        # Filtra DataFrame
        df = Empresa.filter_dataframe(
            filters=[Empresa.estado == SiglaEstadoEnum.SP],
            select_fields=['nome', 'estado']
        )
        
        assert len(df) == 1
        assert df.iloc[0]['nome'] == empresa_data['nome']


class TestEmpresaFieldsMixin:
    """Testes para métodos do _ModelFieldsMixin."""

    def test_field_names(self):
        """Testa o método field_names do mixin."""
        field_names = Empresa.field_names()
        
        assert isinstance(field_names, list)
        assert 'id' in field_names
        assert 'nome' in field_names
        assert 'cnpj' in field_names
        assert 'estado' in field_names

    def test_fields(self):
        """Testa o método fields do mixin."""
        fields = Empresa.fields()
        
        assert isinstance(fields, list)
        assert len(fields) > 0
        # Verifica que retorna objetos Column
        assert all(hasattr(f, 'name') for f in fields)

    def test_get_field(self):
        """Testa o método get_field do mixin."""
        nome_field = Empresa.get_field('nome')
        
        assert nome_field is not None
        assert nome_field.name == 'nome'

    def test_get_field_display_name(self):
        """Testa o método get_field_display_name do mixin."""
        display_name = Empresa.get_field_display_name('nome')
        
        assert display_name == 'Nome'

    def test_validate_field_valid(self):
        """Testa o método validate_field com valor válido."""
        error = Empresa.validate_field('nome', 'Empresa Teste')
        
        assert error is None

    def test_validate_field_null_not_allowed(self):
        """Testa o método validate_field com valor nulo não permitido."""
        error = Empresa.validate_field('nome', None)
        
        assert error is not None
        assert 'não pode ser nulo' in error.lower()

    def test_validate_field_null_allowed(self):
        """Testa o método validate_field com valor nulo permitido."""
        error = Empresa.validate_field('cnpj', None)
        
        assert error is None

    def test_validate_field_string_too_long(self):
        """Testa o método validate_field com string muito longa."""
        nome_longo = 'A' * 300  # Excede o limite de 255
        error = Empresa.validate_field('nome', nome_longo)
        
        assert error is not None
        assert 'muito longo' in error.lower()

    def test_is_valid(self):
        """Testa o método is_valid do mixin."""
        data_valido = {
            'nome': 'Empresa Teste',
            'cnpj': '12345678000123'
        }
        
        assert Empresa.is_valid(data_valido) is True
        
        data_invalido = {
            'nome': None  # nome não pode ser nulo
        }
        
        assert Empresa.is_valid(data_invalido) is False


class TestEmpresaDisplayMixin:
    """Testes para métodos do _ModelDisplayMixin."""

    def test_display_name(self):
        """Testa o método display_name do mixin."""
        display = Empresa.display_name()
        
        assert display == 'Empresa'

    def test_display_name_plural(self):
        """Testa o método display_name_plural do mixin."""
        display = Empresa.display_name_plural()
        
        assert display == 'Empresas'
