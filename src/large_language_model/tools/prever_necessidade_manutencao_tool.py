"""
Tool for predicting maintenance needs using trained machine learning models.
Analyzes sensor readings to predict if equipment requires maintenance.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.sensor import LeituraSensor, Sensor, TipoSensorEnum
from src.database.models.equipamento import Equipamento
from datetime import datetime, timedelta, date
import numpy as np
from src.ml.prediction import carregar_modelo_legado, realizar_previsao


def prever_necessidade_manutencao(
    equipamento_id: int,
    dias_analise: int = 7
) -> str:
    """
    Prevê a necessidade de manutenção de um equipamento usando machine learning.
    
    Analisa as leituras recentes dos sensores do equipamento e usa modelos de
    machine learning treinados para prever se há necessidade de manutenção.
    Retorna a probabilidade de necessidade de manutenção e recomendações.
    
    :param equipamento_id: ID do equipamento a ser analisado
    :param dias_analise: Número de dias de histórico para análise (padrão: 7)
    :return: Predição de manutenção com probabilidade e recomendações
    """
    try:
        # Verificar se o equipamento existe
        equipamento = Equipamento.get_from_id(equipamento_id)
        if not equipamento:
            return f"Erro: Equipamento com ID {equipamento_id} não encontrado."
        
        # Verificar se o equipamento tem sensores
        if not equipamento.sensores or len(equipamento.sensores) == 0:
            return f"Equipamento '{equipamento.nome}' não possui sensores cadastrados."
        
        # Carregar modelo
        try:
            modelo = carregar_modelo_legado()
        except Exception as e:
            return (f"⚠️ Modelo de predição não encontrado: {str(e)}\n"
                   "Execute o treinamento de modelos antes de usar a predição.")
        
        # Coletar leituras recentes de todos os sensores do equipamento
        data_final = date.today()
        data_inicial = data_final - timedelta(days=dias_analise)
        
        # Organizar leituras por tipo de sensor (Temperatura, Vibração, Luminosidade)
        leituras_por_tipo = {
            TipoSensorEnum.TEMPERATURA: [],
            TipoSensorEnum.VIBRACAO: [],
            TipoSensorEnum.LUX: []
        }
        
        sensores_info = []
        for sensor in equipamento.sensores:
            leituras = LeituraSensor.get_leituras_for_sensor(
                sensor_id=sensor.id,
                data_inicial=data_inicial,
                data_final=data_final
            )
            
            if leituras and sensor.tipo_sensor:
                valores = [l.valor for l in leituras]
                tipo = sensor.tipo_sensor.tipo
                
                if tipo in leituras_por_tipo:
                    leituras_por_tipo[tipo].extend(valores)
                    sensores_info.append({
                        'id': sensor.id,
                        'nome': sensor.nome or f'Sensor {sensor.id}',
                        'tipo': tipo,
                        'num_leituras': len(valores)
                    })
        
        # Verificar se temos leituras suficientes
        if not any(leituras_por_tipo.values()):
            return (f"Nenhuma leitura encontrada para os sensores do equipamento '{equipamento.nome}' "
                   f"nos últimos {dias_analise} dias.\n"
                   "Não é possível fazer a predição sem dados recentes.")
        
        # Calcular features (média de cada tipo de sensor)
        # O modelo espera 3 features: Temperatura, Vibração, Luminosidade
        lux_media = np.mean(leituras_por_tipo[TipoSensorEnum.LUX]) if leituras_por_tipo[TipoSensorEnum.LUX] else 0.0
        temp_media = np.mean(leituras_por_tipo[TipoSensorEnum.TEMPERATURA]) if leituras_por_tipo[TipoSensorEnum.TEMPERATURA] else 0.0
        vibracao_media = np.mean(leituras_por_tipo[TipoSensorEnum.VIBRACAO]) if leituras_por_tipo[TipoSensorEnum.VIBRACAO] else 0.0
        
        # Fazer predição usando a função compartilhada
        try:
            resultado = realizar_previsao(modelo, lux_media, temp_media, vibracao_media)
            predicao = resultado['predicao']
            prob_manutencao = resultado['probabilidade_manutencao'] * 100
        except Exception as e:
            return f"Erro ao executar predição: {str(e)}"
        
        # Construir resultado
        output = f"🤖 Predição de Manutenção - Machine Learning\n\n"
        output += f"📦 Equipamento: {equipamento.nome} (ID: {equipamento.id})\n"
        output += f"📅 Período Analisado: {dias_analise} dias\n"
        output += f"📡 Sensores Analisados: {len(sensores_info)}\n\n"
        
        # Detalhes dos sensores
        output += "📊 DADOS COLETADOS:\n"
        for info in sensores_info:
            output += f"   • {info['nome']} ({info['tipo']}): {info['num_leituras']} leitura(s)\n"
        output += "\n"
        
        # Valores médios das features
        output += "📈 VALORES MÉDIOS DETECTADOS:\n"
        output += f"   • Luminosidade: {lux_media:.2f} lux\n"
        output += f"   • Temperatura: {temp_media:.2f} °C\n"
        output += f"   • Vibração: {vibracao_media:.2f}\n\n"
        
        # Resultado da predição
        output += "🎯 RESULTADO DA PREDIÇÃO:\n"
        output += f"   • Probabilidade de Necessidade de Manutenção: {prob_manutencao:.1f}%\n"
        
        if predicao == 1 or prob_manutencao >= 50:
            output += "   • Status: ⚠️ MANUTENÇÃO RECOMENDADA\n\n"
            output += "🔧 RECOMENDAÇÕES:\n"
            output += "   • Agendar manutenção preventiva o mais breve possível\n"
            output += "   • Verificar os sensores com leituras anormais\n"
            output += "   • Monitorar o equipamento com maior frequência\n"
            output += "   • Considerar inspeção técnica detalhada\n"
        else:
            output += "   • Status: ✅ EQUIPAMENTO NORMAL\n\n"
            output += "💡 RECOMENDAÇÕES:\n"
            output += "   • Continuar monitoramento regular\n"
            output += "   • Manter cronograma de manutenção preventiva padrão\n"
            if prob_manutencao > 20:
                output += "   • Atenção: probabilidade moderada - monitorar de perto\n"
        
        return output
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Erro ao prever necessidade de manutenção: {str(e)}\n\nDetalhes: {error_details}"


class PreverNecessidadeManutencaoTool(BaseTool):
    """
    Ferramenta para prever necessidade de manutenção usando Machine Learning.
    Analisa leituras de sensores e retorna probabilidade de necessidade de manutenção.
    """
    
    @property
    def function_declaration(self):
        return prever_necessidade_manutencao
    
    def call_chat_display(self) -> str:
        return "🤖 Analisando dados com Machine Learning..."
    
    def call_result_display(self, result: str) -> str:
        return result
