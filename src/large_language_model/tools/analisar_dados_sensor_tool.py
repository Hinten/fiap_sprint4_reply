"""
Tool for analyzing sensor data and providing statistical summaries.
Calculates metrics like mean, median, std deviation, min, max, and identifies trends.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.sensor import LeituraSensor, Sensor
from datetime import datetime, timedelta, date
import statistics


def analisar_dados_sensor(
    sensor_id: int,
    dias: int = 7
) -> str:
    """
    Analisa os dados de um sensor e retorna um resumo estatístico.
    
    Calcula métricas estatísticas sobre as leituras de um sensor em um período específico,
    incluindo média, mediana, desvio padrão, valores mínimo e máximo, e tendências.
    Também identifica leituras anormais e possíveis problemas.
    
    :param sensor_id: ID do sensor a ser analisado
    :param dias: Número de dias para analisar (padrão: 7 dias)
    :return: String com análise estatística e resumo dos dados
    """
    try:
        # Verificar se o sensor existe
        sensor = Sensor.get_from_id(sensor_id)
        if not sensor:
            return f"Erro: Sensor com ID {sensor_id} não encontrado."
        
        # Calcular período de análise
        data_final = date.today()
        data_inicial = data_final - timedelta(days=dias)
        
        # Buscar leituras do período
        leituras = LeituraSensor.get_leituras_for_sensor(
            sensor_id=sensor_id,
            data_inicial=data_inicial,
            data_final=data_final
        )
        
        if not leituras:
            return f"Nenhuma leitura encontrada para o sensor {sensor.nome or sensor_id} nos últimos {dias} dias."
        
        # Extrair valores
        valores = [leitura.valor for leitura in leituras]
        
        # Calcular estatísticas
        media = statistics.mean(valores)
        mediana = statistics.median(valores)
        minimo = min(valores)
        maximo = max(valores)
        
        # Desvio padrão (se houver dados suficientes)
        desvio_padrao = statistics.stdev(valores) if len(valores) > 1 else 0
        
        # Identificar outliers (valores fora de 2 desvios padrão)
        outliers = []
        if desvio_padrao > 0:
            limiar_superior = media + (2 * desvio_padrao)
            limiar_inferior = media - (2 * desvio_padrao)
            outliers = [v for v in valores if v > limiar_superior or v < limiar_inferior]
        
        # Analisar tendência (comparar primeira e segunda metade)
        meio = len(valores) // 2
        if meio > 0:
            media_primeira_metade = statistics.mean(valores[:meio])
            media_segunda_metade = statistics.mean(valores[meio:])
            diferenca_percentual = ((media_segunda_metade - media_primeira_metade) / media_primeira_metade) * 100 if media_primeira_metade != 0 else 0
            
            if diferenca_percentual > 10:
                tendencia = f"📈 Tendência de AUMENTO ({diferenca_percentual:.1f}%)"
            elif diferenca_percentual < -10:
                tendencia = f"📉 Tendência de REDUÇÃO ({abs(diferenca_percentual):.1f}%)"
            else:
                tendencia = "➡️ Tendência ESTÁVEL"
        else:
            tendencia = "Dados insuficientes para análise de tendência"
        
        # Verificar limiares de manutenção
        alertas = []
        if sensor.limiar_manutencao_maior is not None and maximo > sensor.limiar_manutencao_maior:
            alertas.append(f"⚠️ Valor máximo ({maximo:.2f}) ACIMA do limiar superior ({sensor.limiar_manutencao_maior})")
        
        if sensor.limiar_manutencao_menor is not None and minimo < sensor.limiar_manutencao_menor:
            alertas.append(f"⚠️ Valor mínimo ({minimo:.2f}) ABAIXO do limiar inferior ({sensor.limiar_manutencao_menor})")
        
        # Montar resultado
        tipo_sensor = sensor.tipo_sensor.nome if sensor.tipo_sensor else "Desconhecido"
        unidade = str(sensor.tipo_sensor.tipo) if sensor.tipo_sensor else ""
        
        resultado = f"📊 Análise de Dados - Sensor {sensor.nome or sensor_id}\n\n"
        resultado += f"🏷️ Tipo: {tipo_sensor}\n"
        
        if sensor.equipamento:
            resultado += f"📦 Equipamento: {sensor.equipamento.nome}\n"
        
        resultado += f"📅 Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')} ({dias} dias)\n"
        resultado += f"📈 Total de Leituras: {len(leituras)}\n\n"
        
        resultado += "📊 ESTATÍSTICAS:\n"
        resultado += f"   • Média: {media:.2f} {unidade}\n"
        resultado += f"   • Mediana: {mediana:.2f} {unidade}\n"
        resultado += f"   • Desvio Padrão: {desvio_padrao:.2f}\n"
        resultado += f"   • Mínimo: {minimo:.2f} {unidade}\n"
        resultado += f"   • Máximo: {maximo:.2f} {unidade}\n"
        resultado += f"   • Variação: {maximo - minimo:.2f} {unidade}\n\n"
        
        resultado += f"📈 TENDÊNCIA:\n   {tendencia}\n\n"
        
        if outliers:
            resultado += f"⚠️ ANOMALIAS:\n"
            resultado += f"   • {len(outliers)} leitura(s) anormal(is) detectada(s)\n"
            resultado += f"   • {(len(outliers)/len(valores)*100):.1f}% dos dados são outliers\n\n"
        
        if alertas:
            resultado += "🚨 ALERTAS:\n"
            for alerta in alertas:
                resultado += f"   {alerta}\n"
            resultado += "\n"
        
        # Recomendações
        resultado += "💡 RECOMENDAÇÕES:\n"
        if alertas:
            resultado += "   • Verificar o equipamento devido a leituras fora dos limiares\n"
            resultado += "   • Considerar agendar manutenção preventiva\n"
        elif len(outliers) > len(valores) * 0.1:
            resultado += "   • Muitas leituras anormais detectadas - investigar possível problema no sensor\n"
        elif abs(diferenca_percentual) > 20:
            resultado += "   • Tendência significativa detectada - monitorar de perto\n"
        else:
            resultado += "   • Sensor operando normalmente dentro dos parâmetros esperados\n"
        
        return resultado
        
    except Exception as e:
        return f"Erro ao analisar dados do sensor: {str(e)}"


class AnalisarDadosSensorTool(BaseTool):
    """
    Ferramenta para análise estatística de dados de sensores.
    Calcula métricas, identifica tendências e anomalias, e fornece recomendações.
    """
    
    @property
    def function_declaration(self):
        return analisar_dados_sensor
    
    def call_chat_display(self) -> str:
        return "📊 Analisando dados do sensor..."
    
    def call_result_display(self, result: str) -> str:
        return result
