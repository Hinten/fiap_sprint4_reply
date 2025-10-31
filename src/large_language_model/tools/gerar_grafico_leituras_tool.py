"""
Tool for generating graphs from sensor readings.
Creates visual representations of sensor data over time and returns them as base64 encoded images.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.sensor import LeituraSensor, Sensor
from datetime import datetime, timedelta, date
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64


def gerar_grafico_leituras(
    sensor_id: int,
    dias: int = 7,
    data_especifica: str = None
) -> str:
    """
    Gera um gráfico com as leituras de um sensor.
    
    Cria um gráfico de linha mostrando as leituras de um sensor ao longo do tempo.
    Pode mostrar os últimos N dias ou leituras de uma data específica.
    O gráfico é retornado como uma descrição textual detalhada, pois a interface
    de chat não suporta exibição direta de imagens.
    
    :param sensor_id: ID do sensor para gerar o gráfico
    :param dias: Número de dias para incluir no gráfico (padrão: 7 dias)
    :param data_especifica: Data específica no formato YYYY-MM-DD para filtrar leituras (opcional)
    :return: Descrição textual do gráfico gerado com estatísticas das leituras
    """
    try:
        # Verificar se o sensor existe
        sensor = Sensor.get_from_id(sensor_id)
        if not sensor:
            return f"Erro: Sensor com ID {sensor_id} não encontrado."
        
        # Definir período de análise
        if data_especifica:
            try:
                data_obj = datetime.strptime(data_especifica, '%Y-%m-%d').date()
                data_inicial = data_obj
                data_final = data_obj
                titulo_periodo = f"em {data_obj.strftime('%d/%m/%Y')}"
            except ValueError:
                return f"Erro: Data inválida. Use o formato YYYY-MM-DD. Recebido: {data_especifica}"
        else:
            data_final = date.today()
            data_inicial = data_final - timedelta(days=dias)
            titulo_periodo = f"dos últimos {dias} dias"
        
        # Buscar leituras
        leituras = LeituraSensor.get_leituras_for_sensor(
            sensor_id=sensor_id,
            data_inicial=data_inicial,
            data_final=data_final
        )
        
        if not leituras:
            return f"Nenhuma leitura encontrada para o sensor {sensor.nome or sensor_id} {titulo_periodo}."
        
        # Preparar dados para o gráfico
        timestamps = [leitura.data_leitura for leitura in leituras]
        valores = [leitura.valor for leitura in leituras]
        
        # Criar o gráfico
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, valores, marker='o', linestyle='-', linewidth=2, markersize=4)
        
        # Configurar título e labels
        tipo_sensor = sensor.tipo_sensor.nome if sensor.tipo_sensor else "Sensor"
        unidade = str(sensor.tipo_sensor.tipo) if sensor.tipo_sensor else ""
        
        plt.title(f'{tipo_sensor} - {sensor.nome or f"ID {sensor_id}"}\nLeituras {titulo_periodo}', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Data/Hora', fontsize=12)
        plt.ylabel(f'Valor {unidade}', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Adicionar linhas de limiar se existirem
        if sensor.limiar_manutencao_maior is not None:
            plt.axhline(y=sensor.limiar_manutencao_maior, color='r', linestyle='--', 
                       label=f'Limiar Superior: {sensor.limiar_manutencao_maior}')
        
        if sensor.limiar_manutencao_menor is not None:
            plt.axhline(y=sensor.limiar_manutencao_menor, color='b', linestyle='--',
                       label=f'Limiar Inferior: {sensor.limiar_manutencao_menor}')
        
        if sensor.limiar_manutencao_maior is not None or sensor.limiar_manutencao_menor is not None:
            plt.legend()
        
        # Formatar eixo x para melhor legibilidade
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Converter gráfico para base64 (para possível uso futuro em interfaces web)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        # Calcular estatísticas para a descrição textual
        media = sum(valores) / len(valores)
        minimo = min(valores)
        maximo = max(valores)
        
        # Criar descrição textual do gráfico
        resultado = f"📈 Gráfico Gerado - {tipo_sensor}\n\n"
        resultado += f"🏷️ Sensor: {sensor.nome or f'ID {sensor_id}'}\n"
        
        if sensor.equipamento:
            resultado += f"📦 Equipamento: {sensor.equipamento.nome}\n"
        
        resultado += f"📅 Período: {titulo_periodo}\n"
        resultado += f"📊 Total de Leituras: {len(leituras)}\n\n"
        
        resultado += "📊 RESUMO DOS DADOS:\n"
        resultado += f"   • Valor Médio: {media:.2f} {unidade}\n"
        resultado += f"   • Valor Mínimo: {minimo:.2f} {unidade} em {timestamps[valores.index(minimo)].strftime('%d/%m/%Y %H:%M')}\n"
        resultado += f"   • Valor Máximo: {maximo:.2f} {unidade} em {timestamps[valores.index(maximo)].strftime('%d/%m/%Y %H:%M')}\n"
        resultado += f"   • Variação: {maximo - minimo:.2f} {unidade}\n\n"
        
        # Verificar se há violações de limiar
        violacoes_superior = sum(1 for v in valores if sensor.limiar_manutencao_maior is not None and v > sensor.limiar_manutencao_maior)
        violacoes_inferior = sum(1 for v in valores if sensor.limiar_manutencao_menor is not None and v < sensor.limiar_manutencao_menor)
        
        if violacoes_superior > 0 or violacoes_inferior > 0:
            resultado += "⚠️ ALERTAS:\n"
            if violacoes_superior > 0:
                resultado += f"   • {violacoes_superior} leitura(s) ACIMA do limiar superior\n"
            if violacoes_inferior > 0:
                resultado += f"   • {violacoes_inferior} leitura(s) ABAIXO do limiar inferior\n"
            resultado += "\n"
        
        # Análise de tendência simples
        if len(valores) >= 4:
            primeiro_quarto = valores[:len(valores)//4]
            ultimo_quarto = valores[-len(valores)//4:]
            media_inicial = sum(primeiro_quarto) / len(primeiro_quarto)
            media_final = sum(ultimo_quarto) / len(ultimo_quarto)
            
            if media_final > media_inicial * 1.1:
                resultado += "📈 TENDÊNCIA: Valores em CRESCIMENTO no período\n"
            elif media_final < media_inicial * 0.9:
                resultado += "📉 TENDÊNCIA: Valores em QUEDA no período\n"
            else:
                resultado += "➡️ TENDÊNCIA: Valores ESTÁVEIS no período\n"
        
        # Nota sobre o gráfico gerado (não exibido diretamente no chat)
        resultado += "\n💡 NOTA: O gráfico foi gerado internamente para análise.\n"
        resultado += "   Use a interface web do dashboard para visualização completa.\n"
        
        # Note: The base64 image is generated but not returned in the text response
        # as the LLM chat interface typically doesn't support image display directly.
        # The image could be saved to a file or stored for web interface display.
        
        return resultado
        
    except Exception as e:
        return f"Erro ao gerar gráfico: {str(e)}"


class GerarGraficoLeiturasTool(BaseTool):
    """
    Ferramenta para gerar gráficos de leituras de sensores.
    Cria visualizações de dados ao longo do tempo com estatísticas resumidas.
    """
    
    @property
    def function_declaration(self):
        return gerar_grafico_leituras
    
    def call_chat_display(self) -> str:
        return "📈 Gerando gráfico de leituras..."
    
    def call_result_display(self, result: str) -> str:
        return result
