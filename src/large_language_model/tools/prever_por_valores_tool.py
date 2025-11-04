"""
Tool for predicting maintenance needs using ML with direct sensor values.
Allows prediction without needing an equipment ID, by providing sensor values directly.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.ml.prediction import carregar_modelo_legado, realizar_previsao


def prever_manutencao_por_valores(
    lux: float,
    temperatura: float,
    vibracao: float
) -> str:
    """
    Prevê a necessidade de manutenção usando valores diretos de sensores.
    
    Esta ferramenta permite fazer predições de manutenção fornecendo diretamente
    os valores dos sensores, sem precisar ter um equipamento cadastrado no sistema.
    Útil para simulações e análises rápidas.
    
    :param lux: Valor da intensidade luminosa (lux ou em x10³)
    :param temperatura: Valor da temperatura em graus Celsius
    :param vibracao: Valor da vibração (escala 0-3 típica)
    :return: Predição de manutenção com probabilidade e recomendações
    """
    try:
        # Carregar modelo
        try:
            modelo = carregar_modelo_legado()
        except Exception as e:
            return (f"⚠️ Modelo de predição não encontrado: {str(e)}\n"
                   "Execute o treinamento de modelos antes de usar a predição.")
        
        # Fazer predição usando a função compartilhada
        try:
            resultado = realizar_previsao(modelo, lux, temperatura, vibracao)
            predicao = resultado['predicao']
            prob_manutencao = resultado['probabilidade_manutencao'] * 100
            prob_sem_manutencao = resultado['probabilidade_sem_manutencao'] * 100
        except Exception as e:
            return f"Erro ao executar predição: {str(e)}"
        
        # Construir resultado
        output = f"🤖 Predição de Manutenção - Machine Learning\n\n"
        output += "📊 VALORES DE ENTRADA:\n"
        output += f"   • Luminosidade: {lux:.2f} lux\n"
        output += f"   • Temperatura: {temperatura:.2f} °C\n"
        output += f"   • Vibração: {vibracao:.2f}\n\n"
        
        # Resultado da predição
        output += "🎯 RESULTADO DA PREDIÇÃO:\n"
        
        if resultado['tem_proba']:
            output += f"   • Probabilidade de Manutenção: {prob_manutencao:.1f}%\n"
            output += f"   • Probabilidade Sem Manutenção: {prob_sem_manutencao:.1f}%\n"
        else:
            output += f"   • Resultado: {'MANUTENÇÃO' if predicao == 1 else 'SEM MANUTENÇÃO'}\n"
        
        if predicao == 1 or prob_manutencao >= 50:
            output += "   • Status: ⚠️ MANUTENÇÃO RECOMENDADA\n\n"
            output += "🔧 RECOMENDAÇÕES:\n"
            output += "   • Os valores indicam necessidade de manutenção\n"
            output += "   • Verificar se os valores estão dentro dos limites normais de operação\n"
            output += "   • Considerar agendar manutenção preventiva\n"
            
            # Análise dos valores
            if temperatura > 40 or temperatura < 0:
                output += f"   • ⚠️ Temperatura ({temperatura:.1f}°C) fora do range normal (0-40°C)\n"
            if vibracao > 2.0:
                output += f"   • ⚠️ Vibração alta ({vibracao:.2f}) - valor típico < 2.0\n"
        else:
            output += "   • Status: ✅ CONDIÇÕES NORMAIS\n\n"
            output += "💡 ANÁLISE:\n"
            output += "   • Os valores indicam operação dentro dos padrões normais\n"
            output += "   • Continuar monitoramento regular\n"
            if prob_manutencao > 20:
                output += "   • Atenção: probabilidade moderada - monitorar de perto\n"
        
        output += f"\n📝 Modelo: {type(modelo).__name__}\n"
        
        return output
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Erro ao prever manutenção: {str(e)}\n\nDetalhes: {error_details}"


class PreverManutencaoPorValoresTool(BaseTool):
    """
    Ferramenta para prever manutenção fornecendo valores diretos dos sensores.
    Não requer equipamento cadastrado - aceita valores de lux, temperatura e vibração.
    """
    
    @property
    def function_declaration(self):
        return prever_manutencao_por_valores
    
    def call_chat_display(self) -> str:
        return "🤖 Analisando valores com Machine Learning..."
    
    def call_result_display(self, result: str) -> str:
        return result
