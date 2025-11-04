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
import tempfile
import os
from PIL import Image
from sqlalchemy.orm import joinedload
from src.database.tipos_base.database import Database


def gerar_grafico_leituras(
    sensor_id: int,
    dias: int = 7,
    data_especifica: str = None
) -> dict:
    """
    Gera um gráfico com as leituras de um sensor.
    
    Cria um gráfico de linha mostrando as leituras de um sensor ao longo do tempo.
    Pode mostrar os últimos N dias ou leituras de uma data específica.
    O gráfico é salvo em arquivo temporário e exibido ao usuário.
    
    :param sensor_id: ID do sensor para gerar o gráfico
    :param dias: Número de dias para incluir no gráfico (padrão: 7 dias)
    :param data_especifica: Data específica no formato YYYY-MM-DD para filtrar leituras (opcional)
    :return: Dicionário com estatísticas das leituras e caminho do arquivo temporário
    """
    try:
        # Verificar se o sensor existe
        # Busca o sensor dentro de uma sessão e pré-carrega relacionamentos
        with Database.get_session() as session:
            sensor = session.query(Sensor).options(
                joinedload(Sensor.tipo_sensor),
                joinedload(Sensor.equipamento)
            ).filter(Sensor.id == sensor_id).one_or_none()

        if not sensor:
            return {
                "erro": f"Sensor com ID {sensor_id} não encontrado.",
                "imagem_path": None,
                "obs": "Erro ao gerar gráfico - sensor não encontrado"
            }
        
        # Definir período de análise
        if data_especifica:
            try:
                data_obj = datetime.strptime(data_especifica, '%Y-%m-%d').date()
                data_inicial = data_obj
                data_final = data_obj
                titulo_periodo = f"em {data_obj.strftime('%d/%m/%Y')}"
            except ValueError:
                return {
                    "erro": f"Data inválida. Use o formato YYYY-MM-DD. Recebido: {data_especifica}",
                    "imagem_path": None,
                    "obs": "Erro ao gerar gráfico - formato de data inválido"
                }
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
            return {
                "erro": f"Nenhuma leitura encontrada para o sensor {sensor.nome or sensor_id} {titulo_periodo}.",
                "imagem_path": None,
                "obs": "Erro ao gerar gráfico - sem leituras no período"
            }
        
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
        
        # Converter gráfico para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        # Salvar imagem em arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False)
        temp_file.write(base64.b64decode(image_base64))
        temp_file.close()
        temp_file_path = temp_file.name
        
        plt.close()
        
        # Calcular estatísticas para a descrição textual
        media = sum(valores) / len(valores)
        minimo = min(valores)
        maximo = max(valores)
        
        # Verificar se há violações de limiar
        violacoes_superior = sum(1 for v in valores if sensor.limiar_manutencao_maior is not None and v > sensor.limiar_manutencao_maior)
        violacoes_inferior = sum(1 for v in valores if sensor.limiar_manutencao_menor is not None and v < sensor.limiar_manutencao_menor)
        
        # Análise de tendência simples
        tendencia = "ESTÁVEL"
        if len(valores) >= 4:
            primeiro_quarto = valores[:len(valores)//4]
            ultimo_quarto = valores[-len(valores)//4:]
            media_inicial = sum(primeiro_quarto) / len(primeiro_quarto)
            media_final = sum(ultimo_quarto) / len(ultimo_quarto)
            
            if media_final > media_inicial * 1.1:
                tendencia = "CRESCIMENTO"
            elif media_final < media_inicial * 0.9:
                tendencia = "QUEDA"
        
        # Retornar dicionário com informações
        return {
            "sensor_id": sensor_id,
            "sensor_nome": sensor.nome or f"ID {sensor_id}",
            "tipo_sensor": tipo_sensor,
            "equipamento": sensor.equipamento.nome if sensor.equipamento else None,
            "periodo": titulo_periodo,
            "total_leituras": len(leituras),
            "estatisticas": {
                "media": round(media, 2),
                "minimo": round(minimo, 2),
                "maximo": round(maximo, 2),
                "variacao": round(maximo - minimo, 2),
                "unidade": unidade
            },
            "alertas": {
                "violacoes_superior": violacoes_superior,
                "violacoes_inferior": violacoes_inferior
            },
            "tendencia": tendencia,
            "imagem_path": temp_file_path,
            "obs": "O gráfico está sendo exibido ao usuário na interface"
        }
        
    except Exception as e:
        return {
            "erro": f"Erro ao gerar gráfico: {str(e)}",
            "imagem_path": None,
            "obs": "Erro ao gerar gráfico"
        }


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
    
    def call_result_display(self, result: dict) -> Image.Image:
        """
        Retorna a imagem do gráfico gerado para exibição no chat.
        
        :param result: Dicionário com os dados do resultado, incluindo o caminho da imagem
        :return: Imagem PIL para exibição no Streamlit
        """
        if isinstance(result, dict) and result.get('imagem_path'):
            try:
                # Carregar a imagem do arquivo temporário
                img = Image.open(result['imagem_path'])
                return img
            except Exception as e:
                # Se houver erro ao carregar, retornar mensagem de erro como texto
                return f"Erro ao carregar imagem: {str(e)}"
        
        # Se não tiver imagem, retornar informação de erro
        if isinstance(result, dict) and result.get('erro'):
            return result['erro']
        
        return "Erro ao gerar gráfico"
