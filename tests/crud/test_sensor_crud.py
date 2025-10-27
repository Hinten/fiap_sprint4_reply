"""
Testes CRUD para os modelos de Sensor.

Testa operações básicas de Create, Read, Update e Delete para as entidades
TipoSensor, Sensor e LeituraSensor.
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from src.database.models.sensor import TipoSensor, Sensor, LeituraSensor, TipoSensorEnum
from src.database.models.equipamento import Equipamento
from src.database.tipos_base.database import Database


class TestTipoSensorCRUD:
    """Testes CRUD para TipoSensor."""

    @pytest.fixture
    def tipo_sensor_data(self):
        """Dados de exemplo para criar um tipo de sensor."""
        return {
            'nome': 'Sensor de Temperatura',
            'tipo': TipoSensorEnum.TEMPERATURA
        }

    def test_create_tipo_sensor(self, db_session, tipo_sensor_data):
        """Testa criação de um novo tipo de sensor."""
        tipo_sensor = TipoSensor(**tipo_sensor_data)
        db_session.add(tipo_sensor)
        db_session.commit()
        db_session.refresh(tipo_sensor)

        assert tipo_sensor.id is not None
        assert tipo_sensor.nome == tipo_sensor_data['nome']
        assert tipo_sensor.tipo == tipo_sensor_data['tipo']

    def test_read_tipo_sensor(self, test_database, tipo_sensor_data):
        """Testa leitura de tipo de sensor do banco."""
        with Database.get_session() as session:
            # Criar tipo de sensor
            tipo_sensor = TipoSensor(**tipo_sensor_data)
            session.add(tipo_sensor)
            session.commit()
            session.refresh(tipo_sensor)

            # Ler tipo de sensor
            tipo_sensor_lido = session.query(TipoSensor).filter_by(id=tipo_sensor.id).first()
            assert tipo_sensor_lido is not None
            assert tipo_sensor_lido.nome == tipo_sensor_data['nome']

    def test_update_tipo_sensor(self, test_database, tipo_sensor_data):
        """Testa atualização de tipo de sensor."""
        with Database.get_session() as session:
            # Criar tipo de sensor
            tipo_sensor = TipoSensor(**tipo_sensor_data)
            session.add(tipo_sensor)
            session.commit()
            session.refresh(tipo_sensor)

            # Atualizar tipo de sensor
            novo_nome = 'Sensor de Temperatura Atualizado'
            tipo_sensor.nome = novo_nome
            session.commit()

            # Verificar atualização
            tipo_sensor_atualizado = session.query(TipoSensor).filter_by(id=tipo_sensor.id).first()
            assert tipo_sensor_atualizado.nome == novo_nome

    def test_delete_tipo_sensor(self, test_database, tipo_sensor_data):
        """Testa exclusão de tipo de sensor."""
        with Database.get_session() as session:
            # Criar tipo de sensor
            tipo_sensor = TipoSensor(**tipo_sensor_data)
            session.add(tipo_sensor)
            session.commit()
            session.refresh(tipo_sensor)

            tipo_sensor_id = tipo_sensor.id

            # Excluir tipo de sensor
            session.delete(tipo_sensor)
            session.commit()

            # Verificar exclusão
            tipo_sensor_excluido = session.query(TipoSensor).filter_by(id=tipo_sensor_id).first()
            assert tipo_sensor_excluido is None

    def test_tipo_sensor_unique_constraints(self, test_database, tipo_sensor_data):
        """Testa constraints únicos do tipo de sensor."""
        with Database.get_session() as session:
            # Criar primeiro tipo de sensor
            tipo_sensor1 = TipoSensor(**tipo_sensor_data)
            session.add(tipo_sensor1)
            session.commit()

            # Tentar criar segundo tipo de sensor com mesmo nome (deve falhar)
            tipo_sensor2 = TipoSensor(**tipo_sensor_data)
            session.add(tipo_sensor2)

            with pytest.raises(IntegrityError):  # IntegrityError esperado
                session.commit()

    def test_tipo_sensor_str_method(self, test_database, tipo_sensor_data):
        """Testa mét odo __str__ do tipo de sensor."""
        tipo_sensor = TipoSensor(**tipo_sensor_data)
        tipo_sensor.id = 1  # Simular ID para teste
        assert str(tipo_sensor) == f"1 - {tipo_sensor_data['nome']}"

    def test_tipo_sensor_enum_str(self):
        """Testa mét odo __str__ do enum TipoSensorEnum."""
        assert str(TipoSensorEnum.TEMPERATURA) == "Temperatura (°C)"
        assert str(TipoSensorEnum.LUX) == "Lux (x10³)"
        assert str(TipoSensorEnum.VIBRACAO) == "Vibração"


class TestSensorCRUD:
    """Testes CRUD para Sensor."""

    @pytest.fixture
    def tipo_sensor_fixture(self, test_database):
        """Fixture para criar um tipo de sensor de teste."""
        with Database.get_session() as session:
            tipo_sensor = TipoSensor(
                nome='Tipo Sensor Teste',
                tipo=TipoSensorEnum.TEMPERATURA
            )
            session.add(tipo_sensor)
            session.commit()
            session.refresh(tipo_sensor)
            return tipo_sensor

    @pytest.fixture
    def equipamento_fixture(self, test_database):
        """Fixture para criar um equipamento de teste."""
        with Database.get_session() as session:
            equipamento = Equipamento(
                nome='Equipamento para Sensor',
                modelo='Modelo DEF-789',
                localizacao='Laboratório'
            )
            session.add(equipamento)
            session.commit()
            session.refresh(equipamento)
            return equipamento

    @pytest.fixture
    def sensor_data(self, tipo_sensor_fixture, equipamento_fixture):
        """Dados de exemplo para criar um sensor."""
        return {
            'tipo_sensor_id': tipo_sensor_fixture.id,
            'nome': 'Sensor Temperatura 001',
            'cod_serial': 'TEMP001',
            'descricao': 'Sensor de temperatura ambiente',
            'limiar_manutencao_maior': 50.0,
            'limiar_manutencao_menor': -10.0,
            'data_instalacao': datetime(2023, 2, 20, 14, 30, 0),
            'equipamento_id': equipamento_fixture.id
        }

    def test_create_sensor(self, test_database, sensor_data):
        """Testa criação de um novo sensor."""
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)

            assert sensor.id is not None
            assert sensor.nome == sensor_data['nome']
            assert sensor.cod_serial == sensor_data['cod_serial']
            assert sensor.limiar_manutencao_maior == sensor_data['limiar_manutencao_maior']

    def test_read_sensor(self, test_database, sensor_data):
        """Testa leitura de sensor do banco."""
        with Database.get_session() as session:
            # Criar sensor
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)

            # Ler sensor
            sensor_lido = session.query(Sensor).filter_by(id=sensor.id).first()
            assert sensor_lido is not None
            assert sensor_lido.nome == sensor_data['nome']
            assert sensor_lido.cod_serial == sensor_data['cod_serial']

    def test_update_sensor(self, test_database, sensor_data):
        """Testa atualização de sensor."""
        with Database.get_session() as session:
            # Criar sensor
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)

            # Atualizar sensor
            novo_nome = 'Sensor Temperatura Atualizado'
            sensor.nome = novo_nome
            session.commit()

            # Verificar atualização
            sensor_atualizado = session.query(Sensor).filter_by(id=sensor.id).first()
            assert sensor_atualizado.nome == novo_nome

    def test_delete_sensor(self, test_database, sensor_data):
        """Testa exclusão de sensor."""
        with Database.get_session() as session:
            # Criar sensor
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)

            sensor_id = sensor.id

            # Excluir sensor
            session.delete(sensor)
            session.commit()

            # Verificar exclusão
            sensor_excluido = session.query(Sensor).filter_by(id=sensor_id).first()
            assert sensor_excluido is None

    def test_sensor_relationships(self, test_database, sensor_data, tipo_sensor_fixture, equipamento_fixture):
        """Testa relacionamentos do sensor."""
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()
            session.refresh(sensor)

            # Recarregar objetos com relacionamentos
            sensor = session.query(Sensor).options(
                joinedload(Sensor.tipo_sensor),
                joinedload(Sensor.equipamento)
            ).filter_by(id=sensor.id).first()

            tipo_sensor_fixture = session.query(TipoSensor).options(
                joinedload(TipoSensor.sensors)
            ).filter_by(id=tipo_sensor_fixture.id).first()

            equipamento_fixture = session.query(Equipamento).options(
                joinedload(Equipamento.sensores)
            ).filter_by(id=equipamento_fixture.id).first()

            # Verificar relacionamentos
            assert sensor.tipo_sensor is not None
            assert sensor.tipo_sensor.id == tipo_sensor_fixture.id
            assert sensor.equipamento is not None
            assert sensor.equipamento.id == equipamento_fixture.id

            # Verificar relacionamentos bidirecionais
            assert sensor in tipo_sensor_fixture.sensors
            assert sensor in equipamento_fixture.sensores

    def test_sensor_str_method(self, test_database, sensor_data):
        """Testa mét odo __str__ do sensor."""
        sensor = Sensor(**sensor_data)
        sensor.id = 1  # Simular ID para teste
        assert str(sensor) == f"1 - {sensor_data['nome']}"

    def test_sensor_filter_by_tiposensor(self, test_database, tipo_sensor_fixture, sensor_data):
        """Testa mét odo filter_by_tiposensor."""
        with Database.get_session() as session:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
            session.commit()

            # Filtrar sensores por tipo
            sensores_filtrados = Sensor.filter_by_tiposensor(TipoSensorEnum.TEMPERATURA)
            assert len(sensores_filtrados) > 0
            assert all(s.tipo_sensor.tipo == TipoSensorEnum.TEMPERATURA for s in sensores_filtrados)


class TestLeituraSensorCRUD:
    """Testes CRUD para LeituraSensor."""

    @pytest.fixture
    def sensor_fixture(self, test_database):
        """Fixture para criar um sensor de teste."""
        with Database.get_session() as session:
            # Criar tipo de sensor primeiro
            tipo_sensor = TipoSensor(
                nome='Tipo Sensor Leitura',
                tipo=TipoSensorEnum.TEMPERATURA
            )
            session.add(tipo_sensor)
            session.commit()

            # Criar sensor
            sensor = Sensor(
                tipo_sensor_id=tipo_sensor.id,
                nome='Sensor para Leitura',
                cod_serial='READ001'
            )
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

    def test_create_leitura_sensor(self, test_database, leitura_data):
        """Testa criação de uma nova leitura."""
        with Database.get_session() as session:
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)

            assert leitura.id is not None
            assert leitura.valor == leitura_data['valor']
            assert leitura.data_leitura == leitura_data['data_leitura']
            assert leitura.sensor_id == leitura_data['sensor_id']

    def test_read_leitura_sensor(self, test_database, leitura_data):
        """Testa leitura de leitura do banco."""
        with Database.get_session() as session:
            # Criar leitura
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)

            # Ler leitura
            leitura_lida = session.query(LeituraSensor).filter_by(id=leitura.id).first()
            assert leitura_lida is not None
            assert leitura_lida.valor == leitura_data['valor']

    def test_update_leitura_sensor(self, test_database, leitura_data):
        """Testa atualização de leitura."""
        with Database.get_session() as session:
            # Criar leitura
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)

            # Atualizar leitura
            novo_valor = 30.0
            leitura.valor = novo_valor
            session.commit()

            # Verificar atualização
            leitura_atualizada = session.query(LeituraSensor).filter_by(id=leitura.id).first()
            assert leitura_atualizada.valor == novo_valor

    def test_delete_leitura_sensor(self, test_database, leitura_data):
        """Testa exclusão de leitura."""
        with Database.get_session() as session:
            # Criar leitura
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)

            leitura_id = leitura.id

            # Excluir leitura
            session.delete(leitura)
            session.commit()

            # Verificar exclusão
            leitura_excluida = session.query(LeituraSensor).filter_by(id=leitura_id).first()
            assert leitura_excluida is None

    def test_leitura_sensor_relationship(self, test_database, sensor_fixture, leitura_data):
        """Testa relacionamento entre leitura e sensor."""
        with Database.get_session() as session:
            leitura = LeituraSensor(**leitura_data)
            session.add(leitura)
            session.commit()
            session.refresh(leitura)

            # Recarregar objetos com relacionamentos
            leitura = session.query(LeituraSensor).options(
                joinedload(LeituraSensor.sensor)
            ).filter_by(id=leitura.id).first()

            sensor_fixture = session.query(Sensor).options(
                joinedload(Sensor.leituras)
            ).filter_by(id=sensor_fixture.id).first()

            # Verificar relacionamento bidirecional
            assert leitura.sensor is not None
            assert leitura.sensor.id == sensor_fixture.id
            assert leitura in sensor_fixture.leituras

    def test_leitura_sensor_foreign_key_constraint(self, test_database):
        """Testa constraint de chave estrangeira."""
        with Database.get_session() as session:
            # Habilitar foreign keys no SQLite
            session.execute("PRAGMA foreign_keys = ON")
            
            # Tentar criar leitura com sensor_id inexistente
            leitura = LeituraSensor(
                sensor_id=99999,  # ID inexistente
                valor=15.0,
                data_leitura=datetime.now()
            )
            session.add(leitura)

            with pytest.raises(IntegrityError):  # IntegrityError esperado
                session.commit()
