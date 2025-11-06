from pydantic import BaseModel
from src.database.models.sensor import Sensor, TipoSensor, TipoSensorEnum
from src.database.tipos_base.database import Database
from fastapi import APIRouter

init_router = APIRouter()


class InitSensorRequest(BaseModel):
    serial: str

@init_router.post('/')
def init_sensor(request:InitSensorRequest):
    """
    Cadastra o Sensor na base de dados
    """

    response:dict[str, str] = {
        "status": "success",
        "message": "ESP32 iniciado com sucesso"
    }

    with Database.get_session() as session:

        for tipo in TipoSensorEnum:
            # Verifica se o tipo de sensor já existe
            tipo_sensor = session.query(TipoSensor).filter(
                TipoSensor.tipo == tipo.value
            ).first()

            if not tipo_sensor:
                # Cria o tipo de sensor se não existir
                tipo_sensor = TipoSensor(tipo=tipo.value, nome=str(tipo))
                session.add(tipo_sensor)
                session.commit()


            old_sensor = session.query(Sensor).filter(
                Sensor.cod_serial == request.serial,
                Sensor.tipo_sensor_id == tipo_sensor.id
            ).first()

            if not old_sensor:

                new_sensor = Sensor(
                    nome=f"Sensor {tipo.value} - {request.serial}",
                    cod_serial=request.serial,
                    tipo_sensor_id=tipo_sensor.id,
                    descricao="Sensor cadastrado via API",
                )

                session.add(new_sensor)

            if tipo == TipoSensorEnum.VIBRACAO:
                response['vibration_threshold_min'] = None if not old_sensor else old_sensor.limiar_manutencao_menor
                response['vibration_threshold_max'] = None if not old_sensor else old_sensor.limiar_manutencao_maior

            elif tipo == TipoSensorEnum.TEMPERATURA:
                response['temperature_threshold_min'] = None if not old_sensor else old_sensor.limiar_manutencao_menor
                response['temperature_threshold_max'] = None if not old_sensor else old_sensor.limiar_manutencao_maior

            elif tipo == TipoSensorEnum.LUX:
                response['lux_threshold_min'] = None if not old_sensor else old_sensor.limiar_manutencao_menor
                response['lux_threshold_max'] = None if not old_sensor else old_sensor.limiar_manutencao_maior


        session.commit()

    return response


@init_router.get('/test')
def init_sensor(request:InitSensorRequest):
    """
    Rota de teste para verificar se a API está funcionando
    """
    return {
        "status": "success",
        "message": "Api funcionando"
    }


