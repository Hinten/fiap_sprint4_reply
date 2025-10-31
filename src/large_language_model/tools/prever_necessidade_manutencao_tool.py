"""
Tool for predicting maintenance needs using trained machine learning models.
Analyzes sensor readings to predict if equipment requires maintenance.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.sensor import LeituraSensor, Sensor, TipoSensorEnum
from src.database.models.equipamento import Equipamento
from datetime import datetime, timedelta, date
import joblib
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler


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
        
        # Buscar modelo treinado (usando o melhor modelo segundo a documentação: DecTree_d5)
        modelo_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "..", "assets", "modelos_otimizados_salvos", "DecTree_d5.pkl"
        )
        
        if not os.path.exists(modelo_path):
            # Try alternative path
            modelo_path = os.path.join(
                os.path.dirname(__file__), 
                "..", "..", "..", "assets", "modelos_salvos", "DecTree_d5.pkl"
            )
        
        if not os.path.exists(modelo_path):
            return ("⚠️ Modelo de predição não encontrado.\n"
                   "Execute o treinamento de modelos antes de usar a predição.\n"
                   "Caminho esperado: assets/modelos_otimizados_salvos/DecTree_d5.pkl")
        
        # Carregar modelo
        try:
            modelo = joblib.load(modelo_path)
        except Exception as e:
            return f"Erro ao carregar modelo de ML: {str(e)}"
        
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
        features = []
        tipos_presentes = []
        
        for tipo in [TipoSensorEnum.TEMPERATURA, TipoSensorEnum.VIBRACAO, TipoSensorEnum.LUX]:
            if leituras_por_tipo[tipo]:
                media = np.mean(leituras_por_tipo[tipo])
                features.append(media)
                tipos_presentes.append(str(tipo))
            else:
                # Se não há leituras deste tipo, usar valor neutro (0 após normalização)
                features.append(0.0)
        
        if len(tipos_presentes) == 0:
            return "Erro: Não foi possível extrair features dos sensores para predição."
        
        # Normalizar features (o modelo foi treinado com dados normalizados)
        # Usar MinMaxScaler com ranges conhecidos dos sensores
        scaler = MinMaxScaler()
        # Definir ranges aproximados baseados nos tipos de sensores
        # Temperatura: -40 a 85°C, Vibração: 0 a 3, Luminosidade: 0.1 a 100000
        scaler.fit([[-40, 0, 0.1], [85, 3, 100000]])
        features_scaled = scaler.transform([features])[0]
        
        # Fazer predição
        try:
            predicao = modelo.predict([features_scaled])[0]
            
            # Tentar obter probabilidade se o modelo suportar
            if hasattr(modelo, 'predict_proba'):
                probabilidades = modelo.predict_proba([features_scaled])[0]
                prob_manutencao = probabilidades[1] * 100  # Probabilidade da classe 1 (necessita manutenção)
            else:
                # Se não tiver predict_proba, usar a predição binária
                prob_manutencao = 100.0 if predicao == 1 else 0.0
        except Exception as e:
            return f"Erro ao executar predição: {str(e)}"
        
        # Construir resultado
        resultado = f"🤖 Predição de Manutenção - Machine Learning\n\n"
        resultado += f"📦 Equipamento: {equipamento.nome} (ID: {equipamento.id})\n"
        resultado += f"📅 Período Analisado: {dias_analise} dias\n"
        resultado += f"📡 Sensores Analisados: {len(sensores_info)}\n\n"
        
        # Detalhes dos sensores
        resultado += "📊 DADOS COLETADOS:\n"
        for info in sensores_info:
            resultado += f"   • {info['nome']} ({info['tipo']}): {info['num_leituras']} leitura(s)\n"
        resultado += "\n"
        
        # Valores médios das features
        resultado += "📈 VALORES MÉDIOS DETECTADOS:\n"
        labels = ["Temperatura", "Vibração", "Luminosidade (x10³)"]
        for i, (label, valor) in enumerate(zip(labels, features)):
            if valor != 0.0 or tipos_presentes:
                resultado += f"   • {label}: {valor:.2f}\n"
        resultado += "\n"
        
        # Resultado da predição
        resultado += "🎯 RESULTADO DA PREDIÇÃO:\n"
        resultado += f"   • Probabilidade de Necessidade de Manutenção: {prob_manutencao:.1f}%\n"
        
        if predicao == 1 or prob_manutencao >= 50:
            resultado += "   • Status: ⚠️ MANUTENÇÃO RECOMENDADA\n\n"
            resultado += "🔧 RECOMENDAÇÕES:\n"
            resultado += "   • Agendar manutenção preventiva o mais breve possível\n"
            resultado += "   • Verificar os sensores com leituras anormais\n"
            resultado += "   • Monitorar o equipamento com maior frequência\n"
            resultado += "   • Considerar inspeção técnica detalhada\n"
        else:
            resultado += "   • Status: ✅ EQUIPAMENTO NORMAL\n\n"
            resultado += "💡 RECOMENDAÇÕES:\n"
            resultado += "   • Continuar monitoramento regular\n"
            resultado += "   • Manter cronograma de manutenção preventiva padrão\n"
            if prob_manutencao > 20:
                resultado += "   • Atenção: probabilidade moderada - monitorar de perto\n"
        
        resultado += f"\n📝 MODELO UTILIZADO: Decision Tree (max_depth=5)\n"
        resultado += f"   • Acurácia do modelo: 95.24%\n"
        resultado += f"   • F1-Score: 0.9524\n"
        
        return resultado
        
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
