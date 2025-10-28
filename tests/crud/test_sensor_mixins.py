"""
Testes para validar os métodos dos mixins dos modelos de Sensor.

Testa métodos herdados de:
- _ModelCrudMixin
- _ModelSerializationMixin
- _ModelFieldsMixin
- _ModelDisplayMixin

Para os modelos: TipoSensor, Sensor, LeituraSensor
"""
import pytest
from datetime import datetime
from src.database.models.sensor import TipoSensor, Sensor, LeituraSensor, TipoSensorEnum
from src.database.models.equipamento import Equipamento
from src.database.tipos_base.database import Database


class TestTipoSensorCrudMixin:
    """Testes para métodos do _ModelCrudMixin no modelo TipoSensor."""

    @pytest.fixture
    def tipo_sensor_data(self):
        """Dados de exemplo para criar um tipo de sensor."""
        return {
            'nome': 'Sensor de Temperatura',
            'tipo': TipoSensorEnum.TEMPERATURA
        }

    def test_get_from_id(self, test_database, tipo_sensor_data):
        """Testa o método get_from_id do mixin."""
        with Database.get_session() as session:
            tipo_sensor = TipoSensor(**tipo_sensor_data)
            session.add(tipo_sensor)
            session.commit()
            session.refresh(tipo_sensor)
            tipo_sensor_id = tipo_sensor.id

        # Busca usando o método do mixin
        tipo_encontrado = TipoSensor.get_from_id(tipo_sensor_id)
        assert tipo_encontrado is not None
        assert tipo_encontrado.id == tipo_sensor_id
        assert tipo_encontrado.nome == tipo_sensor_data['nome']

    def test_save(self, test_database, tipo_sensor_data):
        """Testa o método save do mixin."""
        tipo_sensor = TipoSensor(**tipo_sensor_data)
        
        # Salva usando o método do mixin
        tipo_salvo = tipo_sensor.save()
        
        assert tipo_salvo.id is not None
        assert tipo_salvo.nome == tipo_sensor_data['nome']

    def test_count(self, test_database, tipo_sensor_data):
        """Testa o método count do mixin."""
        assert TipoSensor.count() == 0
        
        with Database.get_session() as session:
            tipo_sensor = TipoSensor(**tipo_sensor_data)
            session.add(tipo_sensor)
            session.commit()

        assert TipoSensor.count() == 1


class TestTipoSensorSerializationMixin:
    """Testes para métodos do _ModelSerializationMixin no modelo TipoSensor."""

    @pytest.fixture
    def tipo_sensor_data(self):
        """Dados de exemplo para criar um tipo de sensor."""
        return {
            'nome': 'Sensor de Temperatura',
            'tipo': TipoSensorEnum.TEMPERATURA
        }

    def test_to_dict(self, test_database, tipo_sensor_data):
        """Testa o método to_dict do mixin."""
        with Database.get_session() as session:
            tipo_sensor = TipoSensor(**tipo_sensor_data)
            session.add(tipo_sensor)
            session.commit()
            session.refresh(tipo_sensor)

        tipo_dict = tipo_sensor.to_dict()
        
        assert isinstance(tipo_dict, dict)
        assert tipo_dict['nome'] == tipo_sensor_data['nome']
        assert tipo_dict['tipo'] == tipo_sensor_data['tipo']

    def test_from_dict(self, test_database, tipo_sensor_data):
        """Testa o método from_dict do mixin."""
        tipo_sensor = TipoSensor.from_dict(tipo_sensor_data)
        
        assert tipo_sensor.nome == tipo_sensor_data['nome']
        assert tipo_sensor.tipo == tipo_sensor_data['tipo']


class TestTipoSensorFieldsMixin:
    """Testes para métodos do _ModelFieldsMixin no modelo TipoSensor."""

    def test_field_names(self):
        """Testa o método field_names do mixin."""
        field_names = TipoSensor.field_names()
        
        assert 'id' in field_names
        assert 'nome' in field_names
        assert 'tipo' in field_names

    def test_get_field(self):
        """Testa o método get_field do mixin."""
        nome_field = TipoSensor.get_field('nome')
        assert nome_field.name == 'nome'


class TestTipoSensorDisplayMixin:
    """Testes para métodos do _ModelDisplayMixin no modelo TipoSensor."""

    def test_display_name(self):
        """Testa o método display_name do mixin."""
        display = TipoSensor.display_name()
        assert display == 'Tipo de Sensor'

    def test_display_name_plural(self):
        """Testa o método display_name_plural do mixin."""
        display = TipoSensor.display_name_plural()
        assert display == 'Tipos de Sensores'


class TestSensorCrudMixin:
    """Testes para métodos do _ModelCrudMixin no modelo Sensor."""

    @pytest.fixture
    def tipo_sensor_fixture(self, test_database):
        """Fixture para criar um tipo de sensor."""
        with Database.get_session() as session:
            tipo_sensor = TipoSensor(nome='Tipo Teste', tipo=TipoSensorEnum.TEMPERATURA)
            session.add(tipo_sensor)
            session.commit()
            session.refresh(tipo_sensor)
            return tipo_sensor

    @pytest.fixture
    def equipamento_fixture(self, test_database):
        """Fixture para criar um equipamento."""
        with Database.get_session() as session:
            equipamento = Equipamento(nome='Equipamento Sensor Teste', modelo='ABC-123', localizacao='Lab')
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)
            return equipamento

    @pytest.fixture
    def sensor_data(self, tipo_sensor_fixture, equipamento_fixture):
        """Dados de exemplo para criar um sensor."""
        return {
            'tipo_sensor_id': tipo_sensor_fixture.id,
            'nome': 'Sensor Teste 001',
            'cod_serial': 'TEMP001',
            'descricao': 'Sensor de teste',
            'equipamento_id': equipamento_fixture.id
        }

    def test_get_from_id(self, test_database, sensor_data):
        """Testa o método get_from_id do mixin."""
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)
            sensor_id = sensor.id

        sensor_encontrado = Sensor.get_from_id(sensor_id)
        assert sensor_encontrado is not None
        assert sensor_encontrado.id == sensor_id
        assert sensor_encontrado.nome == sensor_data['nome']

    def test_all(self, test_database, sensor_data):
        """Testa o método all do mixin."""
        with Database.get_session() as session:
            sensor1 = Sensor(**sensor_data)
            session.add(sensor1)
            
            sensor_data2 = sensor_data.copy()
            sensor_data2['nome'] = 'Sensor Dois'
            sensor2 = Sensor(**sensor_data2)
            session.add(sensor2)
            session.commit()

        todos_sensores = Sensor.all()
        assert len(todos_sensores) == 2

    def test_save(self, test_database, sensor_data):
        """Testa o método save do mixin."""
        sensor = Sensor(**sensor_data)
        sensor_salvo = sensor.save()
        
        assert sensor_salvo.id is not None
        assert sensor_salvo.nome == sensor_data['nome']

    def test_update(self, test_database, sensor_data):
        """Testa o método update do mixin."""
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)
            sensor_id = sensor.id

        sensor_busca = Sensor.get_from_id(sensor_id)
        sensor_busca.update(nome='Sensor Atualizado')
        
        with Database.get_session() as session:
            sensor_db = session.query(Sensor).filter_by(id=sensor_id).first()
            assert sensor_db.nome == 'Sensor Atualizado'

    def test_delete(self, test_database, sensor_data):
        """Testa o método delete do mixin."""
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)
            sensor_id = sensor.id

        sensor_busca = Sensor.get_from_id(sensor_id)
        sensor_busca.delete()
        
        with Database.get_session() as session:
            sensor_db = session.query(Sensor).filter_by(id=sensor_id).first()
            assert sensor_db is None

    def test_count(self, test_database, sensor_data):
        """Testa o método count do mixin."""
        assert Sensor.count() == 0
        
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()

        assert Sensor.count() == 1

    def test_first(self, test_database, sensor_data):
        """Testa o método first do mixin."""
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()

        primeiro = Sensor.first()
        assert primeiro is not None
        assert primeiro.nome == sensor_data['nome']

    def test_last(self, test_database, sensor_data):
        """Testa o método last do mixin."""
        with Database.get_session() as session:
            sensor1 = Sensor(**sensor_data)
            session.add(sensor1)
            
            sensor_data2 = sensor_data.copy()
            sensor_data2['nome'] = 'Sensor Último'
            sensor2 = Sensor(**sensor_data2)
            session.add(sensor2)
            session.commit()

        ultimo = Sensor.last()
        assert ultimo is not None
        assert ultimo.nome == 'Sensor Último'


class TestSensorSerializationMixin:
    """Testes para métodos do _ModelSerializationMixin no modelo Sensor."""

    @pytest.fixture
    def tipo_sensor_fixture(self, test_database):
        """Fixture para criar um tipo de sensor."""
        with Database.get_session() as session:
            tipo_sensor = TipoSensor(nome='Tipo Teste', tipo=TipoSensorEnum.TEMPERATURA)
            session.add(tipo_sensor)
            session.commit()
            session.refresh(tipo_sensor)
            return tipo_sensor

    @pytest.fixture
    def sensor_data(self, tipo_sensor_fixture):
        """Dados de exemplo para criar um sensor."""
        return {
            'tipo_sensor_id': tipo_sensor_fixture.id,
            'nome': 'Sensor Teste',
            'cod_serial': 'TEMP001'
        }

    def test_to_dict(self, test_database, sensor_data):
        """Testa o método to_dict do mixin."""
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)

        sensor_dict = sensor.to_dict()
        
        assert isinstance(sensor_dict, dict)
        assert sensor_dict['nome'] == sensor_data['nome']

    def test_from_dict(self, test_database, sensor_data):
        """Testa o método from_dict do mixin."""
        sensor = Sensor.from_dict(sensor_data)
        
        assert sensor.nome == sensor_data['nome']

    def test_as_dataframe_all(self, test_database, sensor_data):
        """Testa o método as_dataframe_all do mixin."""
        with Database.get_session() as session:
            sensor1 = Sensor(**sensor_data)
            session.add(sensor1)
            
            sensor_data2 = sensor_data.copy()
            sensor_data2['nome'] = 'Sensor Dois'
            sensor2 = Sensor(**sensor_data2)
            session.add(sensor2)
            session.commit()

        df = Sensor.as_dataframe_all()
        
        assert len(df) == 2
        assert 'nome' in df.columns


class TestSensorFieldsMixin:
    """Testes para métodos do _ModelFieldsMixin no modelo Sensor."""

    def test_field_names(self):
        """Testa o método field_names do mixin."""
        field_names = Sensor.field_names()
        
        assert 'id' in field_names
        assert 'nome' in field_names
        assert 'tipo_sensor_id' in field_names

    def test_validate_field(self):
        """Testa o método validate_field do mixin."""
        error = Sensor.validate_field('nome', 'Sensor Teste')
        assert error is None


class TestSensorDisplayMixin:
    """Testes para métodos do _ModelDisplayMixin no modelo Sensor."""

    def test_display_name_plural(self):
        """Testa o método display_name_plural do mixin."""
        display = Sensor.display_name_plural()
        assert display == 'Sensores'


class TestLeituraSensorCrudMixin:
    """Testes para métodos do _ModelCrudMixin no modelo LeituraSensor."""

    @pytest.fixture
    def sensor_fixture(self, test_database):
        """Fixture para criar um sensor."""
        with Database.get_session() as session:
            tipo_sensor = TipoSensor(nome='Tipo Leitura', tipo=TipoSensorEnum.TEMPERATURA)
            session.add(tipo_sensor)
            session.commit()
            
            sensor = Sensor(tipo_sensor_id=tipo_sensor.id, nome='Sensor Leitura', cod_serial='READ001')
            session.add(sensor)
            session.commit()
            session.refresh(sensor)
            return sensor

    @pytest.fixture
    def leitura_data(self, sensor_fixture):
        """Dados de exemplo para criar uma leitura."""
        return {
            'sensor_id': sensor_fixture.id,
            'valor': 25.5,
            'data_leitura': datetime(2024, 1, 15, 10, 30, 45)
        }

    def test_get_from_id(self, test_database, leitura_data):
        """Testa o método get_from_id do mixin."""
        with Database.get_session() as session:
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)
            leitura_id = leitura.id

        leitura_encontrada = LeituraSensor.get_from_id(leitura_id)
        assert leitura_encontrada is not None
        assert leitura_encontrada.id == leitura_id
        assert leitura_encontrada.valor == leitura_data['valor']

    def test_all(self, test_database, leitura_data):
        """Testa o método all do mixin."""
        with Database.get_session() as session:
            leitura1 = LeituraSensor(**leitura_data)
            session.add(leitura1)
            
            leitura_data2 = leitura_data.copy()
            leitura_data2['valor'] = 30.0
            leitura2 = LeituraSensor(**leitura_data2)
            session.add(leitura2)
            session.commit()

        todas_leituras = LeituraSensor.all()
        assert len(todas_leituras) == 2

    def test_save(self, test_database, leitura_data):
        """Testa o método save do mixin."""
        leitura = LeituraSensor(**leitura_data)
        leitura_salva = leitura.save()
        
        assert leitura_salva.id is not None
        assert leitura_salva.valor == leitura_data['valor']

    def test_update(self, test_database, leitura_data):
        """Testa o método update do mixin."""
        with Database.get_session() as session:
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)
            leitura_id = leitura.id

        leitura_busca = LeituraSensor.get_from_id(leitura_id)
        leitura_busca.update(valor=30.0)
        
        with Database.get_session() as session:
            leitura_db = session.query(LeituraSensor).filter_by(id=leitura_id).first()
            assert leitura_db.valor == 30.0

    def test_delete(self, test_database, leitura_data):
        """Testa o método delete do mixin."""
        with Database.get_session() as session:
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)
            leitura_id = leitura.id

        leitura_busca = LeituraSensor.get_from_id(leitura_id)
        leitura_busca.delete()
        
        with Database.get_session() as session:
            leitura_db = session.query(LeituraSensor).filter_by(id=leitura_id).first()
            assert leitura_db is None

    def test_count(self, test_database, leitura_data):
        """Testa o método count do mixin."""
        assert LeituraSensor.count() == 0
        
        with Database.get_session() as session:
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()

        assert LeituraSensor.count() == 1

    def test_first(self, test_database, leitura_data):
        """Testa o método first do mixin."""
        with Database.get_session() as session:
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()

        primeira = LeituraSensor.first()
        assert primeira is not None
        assert primeira.valor == leitura_data['valor']


class TestLeituraSensorSerializationMixin:
    """Testes para métodos do _ModelSerializationMixin no modelo LeituraSensor."""

    @pytest.fixture
    def sensor_fixture(self, test_database):
        """Fixture para criar um sensor."""
        with Database.get_session() as session:
            tipo_sensor = TipoSensor(nome='Tipo Leitura', tipo=TipoSensorEnum.TEMPERATURA)
            session.add(tipo_sensor)
            session.commit()
            
            sensor = Sensor(tipo_sensor_id=tipo_sensor.id, nome='Sensor Leitura', cod_serial='READ001')
            session.add(sensor)
            session.commit()
            session.refresh(sensor)
            return sensor

    @pytest.fixture
    def leitura_data(self, sensor_fixture):
        """Dados de exemplo para criar uma leitura."""
        return {
            'sensor_id': sensor_fixture.id,
            'valor': 25.5,
            'data_leitura': datetime(2024, 1, 15, 10, 30, 45)
        }

    def test_to_dict(self, test_database, leitura_data):
        """Testa o método to_dict do mixin."""
        with Database.get_session() as session:
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)

        leitura_dict = leitura.to_dict()
        
        assert isinstance(leitura_dict, dict)
        assert leitura_dict['valor'] == leitura_data['valor']

    def test_from_dict(self, test_database, leitura_data):
        """Testa o método from_dict do mixin."""
        leitura = LeituraSensor.from_dict(leitura_data)
        
        assert leitura.valor == leitura_data['valor']


class TestLeituraSensorFieldsMixin:
    """Testes para métodos do _ModelFieldsMixin no modelo LeituraSensor."""

    def test_field_names(self):
        """Testa o método field_names do mixin."""
        field_names = LeituraSensor.field_names()
        
        assert 'id' in field_names
        assert 'sensor_id' in field_names
        assert 'valor' in field_names
        assert 'data_leitura' in field_names


class TestLeituraSensorDisplayMixin:
    """Testes para métodos do _ModelDisplayMixin no modelo LeituraSensor."""

    def test_display_name(self):
        """Testa o método display_name do mixin."""
        display = LeituraSensor.display_name()
        assert display == 'Leitura de Sensor'

    def test_display_name_plural(self):
        """Testa o método display_name_plural do mixin."""
        display = LeituraSensor.display_name_plural()
        assert display == 'Leituras de Sensores'
