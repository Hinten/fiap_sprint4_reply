"""
Tool for listing all installed sensors in the system.
Provides information about sensors including ID, name, type, equipment association, and thresholds.
"""
from sqlalchemy import inspect
from sqlalchemy.orm import selectinload

from src.database.tipos_base.database import Database
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.sensor import Sensor
from typing import Optional


def listar_sensores(equipamento_id: Optional[int] = None) -> str:
    """
    Lista todos os sensores instalados no sistema.
    
    Retorna informações detalhadas sobre cada sensor cadastrado,
    incluindo ID, nome, tipo (temperatura, vibração, luminosidade),
    equipamento associado, e limiares de manutenção.
    
    :param equipamento_id: ID do equipamento (opcional). Se fornecido, lista apenas sensores deste equipamento.
    :return: String formatada com a lista de sensores e suas informações
    """
    try:
        if equipamento_id is not None:
            # Filter sensors by equipment
            with Database.get_session() as session:
                query = session.query(Sensor).filter(Sensor.equipamento_id == equipamento_id)

                for rel in inspect(Sensor).mapper.relationships:
                    query = query.options(selectinload(getattr(Sensor, rel.key)))

                sensores = query.order_by(Sensor.id).all()
            
            if not sensores:
                return f"Nenhum sensor encontrado para o equipamento ID {equipamento_id}."
        else:
            sensores = Sensor.all()
        
        if not sensores:
            return "Nenhum sensor cadastrado no sistema."
        
        titulo = f"Total de {len(sensores)} sensor(es) cadastrado(s)"
        if equipamento_id:
            titulo += f" no equipamento ID {equipamento_id}"
        resultado = titulo + ":\n\n"
        
        for sensor in sensores:
            resultado += f"📡 ID: {sensor.id}\n"
            resultado += f"   Nome: {sensor.nome or 'Sem nome'}\n"
            
            if sensor.tipo_sensor:
                resultado += f"   Tipo: {sensor.tipo_sensor.nome} ({sensor.tipo_sensor.tipo})\n"
            
            if sensor.equipamento:
                resultado += f"   Equipamento: {sensor.equipamento.nome} (ID: {sensor.equipamento.id})\n"
            
            if sensor.cod_serial:
                resultado += f"   Código Serial: {sensor.cod_serial}\n"
            
            if sensor.limiar_manutencao_maior is not None:
                resultado += f"   Limiar Superior: {sensor.limiar_manutencao_maior}\n"
            
            if sensor.limiar_manutencao_menor is not None:
                resultado += f"   Limiar Inferior: {sensor.limiar_manutencao_menor}\n"
            
            if sensor.data_instalacao:
                data_formatada = sensor.data_instalacao.strftime('%d/%m/%Y')
                resultado += f"   Data de Instalação: {data_formatada}\n"
            
            if sensor.descricao:
                resultado += f"   Descrição: {sensor.descricao}\n"
            
            resultado += "\n"
        
        return resultado.strip()
        
    except Exception as e:
        return f"Erro ao listar sensores: {str(e)}"


class ListarSensoresTool(BaseTool):
    """
    Ferramenta para listar todos os sensores cadastrados no sistema.
    Pode filtrar por equipamento específico ou listar todos os sensores.
    """
    
    @property
    def function_declaration(self):
        return listar_sensores
    
    def call_chat_display(self) -> str:
        return "📡 Listando sensores cadastrados..."
    
    def call_result_display(self, result: str) -> str:
        return f"✅ Sensores:\n{result}"
