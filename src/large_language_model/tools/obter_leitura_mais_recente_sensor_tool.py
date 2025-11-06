"""
Tool for getting the most recent sensor reading by sensor ID.
Retrieves the latest reading from a specific sensor including timestamp and value.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.sensor import LeituraSensor, Sensor
from src.database.tipos_base.database import Database
from sqlalchemy.orm import joinedload


def obter_leitura_mais_recente_sensor(sensor_id: int) -> str:
    """
    Obtém a leitura mais recente de um sensor específico.
    
    Retorna informações sobre a última leitura registrada para o sensor,
    incluindo o valor lido, data/hora da leitura, tipo de sensor e equipamento
    associado. Útil para monitoramento em tempo real e verificação do status atual.
    
    :param sensor_id: ID do sensor a ser consultado
    :return: String formatada com informações da leitura mais recente
    """
    try:
        # Verificar se o sensor existe e carregar informações relacionadas
        with Database.get_session() as session:
            sensor = session.query(Sensor).options(
                joinedload(Sensor.tipo_sensor),
                joinedload(Sensor.equipamento)
            ).filter(Sensor.id == sensor_id).one_or_none()

        if not sensor:
            return f"Erro: Sensor com ID {sensor_id} não encontrado."
        
        # Buscar a leitura mais recente
        with Database.get_session() as session:
            leitura_recente = session.query(LeituraSensor).filter(
                LeituraSensor.sensor_id == sensor_id
            ).order_by(LeituraSensor.data_leitura.desc()).first()
        
        if not leitura_recente:
            return f"Nenhuma leitura encontrada para o sensor {sensor.nome or sensor_id}."
        
        # Formatar resultado
        resultado = "📡 Leitura Mais Recente do Sensor\n\n"
        
        # Informações do sensor
        resultado += f"🔹 Sensor ID: {sensor.id}\n"
        resultado += f"🔹 Nome: {sensor.nome or 'N/A'}\n"
        resultado += f"🔹 Tipo: {sensor.tipo_sensor.tipo if sensor.tipo_sensor else 'N/A'}\n"
        
        if sensor.equipamento:
            resultado += f"🔹 Equipamento: {sensor.equipamento.nome} (ID: {sensor.equipamento.id})\n"
        
        resultado += "\n"
        
        # Informações da leitura
        resultado += "📊 ÚLTIMA LEITURA:\n"
        resultado += f"   • Data/Hora: {leitura_recente.data_leitura.strftime('%d/%m/%Y %H:%M:%S')}\n"
        
        # Formatar valor com unidade apropriada
        tipo_str = str(sensor.tipo_sensor.tipo) if sensor.tipo_sensor else ""
        valor_formatado = f"{leitura_recente.valor:.2f}"
        
        # Adicionar símbolo de unidade baseado no tipo de sensor
        if sensor.tipo_sensor:
            if "Temperatura" in tipo_str:
                valor_formatado += " °C"
            elif "Lux" in tipo_str:
                # Valor já está em lux (x10³ está no nome do tipo)
                valor_formatado += " lux"
            elif "Vibração" in tipo_str:
                valor_formatado += " (escala 0-3)"
        
        resultado += f"   • Valor: {valor_formatado}\n"
        
        # Adicionar alerta se o valor parecer anormal (baseado em ranges conhecidos)
        if sensor.tipo_sensor:
            alerta = None
            valor = leitura_recente.valor
            
            if "Temperatura" in tipo_str:
                if valor > 50:
                    alerta = "⚠️ Temperatura muito alta!"
                elif valor < 0:
                    alerta = "⚠️ Temperatura muito baixa!"
            elif "Vibração" in tipo_str:
                if valor > 2.5:
                    alerta = "⚠️ Vibração elevada - possível problema!"
            elif "Lux" in tipo_str:
                if valor > 80000:
                    alerta = "⚠️ Luminosidade muito alta!"
                elif valor < 100:
                    alerta = "⚠️ Luminosidade muito baixa!"
            
            if alerta:
                resultado += f"\n{alerta}\n"
        
        # Informação sobre idade da leitura
        from datetime import datetime
        idade = datetime.now() - leitura_recente.data_leitura
        
        if idade.days > 0:
            resultado += f"\n⏰ Última atualização há {idade.days} dia(s)"
        elif idade.seconds > 3600:
            horas = idade.seconds // 3600
            resultado += f"\n⏰ Última atualização há {horas} hora(s)"
        elif idade.seconds > 60:
            minutos = idade.seconds // 60
            resultado += f"\n⏰ Última atualização há {minutos} minuto(s)"
        else:
            resultado += f"\n⏰ Última atualização há {idade.seconds} segundo(s)"
        
        return resultado
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Erro ao obter leitura do sensor: {str(e)}\n\nDetalhes: {error_details}"


class ObterLeituraMaisRecenteSensorTool(BaseTool):
    """
    Ferramenta para obter a leitura mais recente de um sensor.
    Retorna valor, timestamp e informações contextuais do sensor.
    """
    
    @property
    def function_declaration(self):
        return obter_leitura_mais_recente_sensor
    
    def call_chat_display(self) -> str:
        return "📡 Consultando leitura mais recente do sensor..."
    
    def call_result_display(self, result: str) -> str:
        return result
