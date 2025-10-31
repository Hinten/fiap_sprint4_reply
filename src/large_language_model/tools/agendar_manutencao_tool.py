"""
Tool for scheduling new maintenance for equipment.
Creates maintenance records with predicted dates and reasons.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.manutencao_equipamento import ManutencaoEquipamento
from src.database.models.equipamento import Equipamento
from datetime import datetime


def agendar_manutencao(
    equipamento_id: int,
    data_previsao: str,
    motivo: str,
    descricao: str = None
) -> str:
    """
    Agenda uma nova manutenção para um equipamento.
    
    Cria um registro de manutenção preventiva ou corretiva no sistema,
    definindo a data prevista e o motivo da manutenção.
    
    :param equipamento_id: ID do equipamento que receberá manutenção
    :param data_previsao: Data prevista para manutenção no formato YYYY-MM-DD ou DD/MM/YYYY
    :param motivo: Motivo da manutenção (ex: "Manutenção preventiva", "Sensor de temperatura fora do limiar")
    :param descricao: Descrição detalhada da manutenção (opcional)
    :return: String confirmando o agendamento ou mensagem de erro
    """
    try:
        # Validar se o equipamento existe
        equipamento = Equipamento.get_from_id(equipamento_id)
        if not equipamento:
            return f"Erro: Equipamento com ID {equipamento_id} não encontrado."
        
        # Parse da data
        try:
            # Try YYYY-MM-DD format first
            if '-' in data_previsao and len(data_previsao.split('-')[0]) == 4:
                data_obj = datetime.strptime(data_previsao, '%Y-%m-%d')
            # Try DD/MM/YYYY format
            elif '/' in data_previsao:
                data_obj = datetime.strptime(data_previsao, '%d/%m/%Y')
            # Try YYYY-MM-DD with time
            elif 'T' in data_previsao or ' ' in data_previsao:
                data_obj = datetime.fromisoformat(data_previsao.replace('T', ' '))
            else:
                return f"Erro: Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY. Recebido: {data_previsao}"
        except ValueError as e:
            return f"Erro ao converter data '{data_previsao}': {str(e)}"
        
        # Verificar se a data não está no passado
        if data_obj.date() < datetime.now().date():
            return f"Aviso: A data prevista ({data_obj.strftime('%d/%m/%Y')}) está no passado. Deseja continuar mesmo assim?"
        
        # Criar registro de manutenção
        manutencao = ManutencaoEquipamento(
            equipamento_id=equipamento_id,
            data_previsao_manutencao=data_obj,
            motivo=motivo,
            descricao=descricao
        )
        
        # Salvar no banco de dados
        manutencao.save()
        
        data_formatada = data_obj.strftime('%d/%m/%Y')
        
        resultado = f"✅ Manutenção agendada com sucesso!\n\n"
        resultado += f"📋 ID da Manutenção: {manutencao.id}\n"
        resultado += f"📦 Equipamento: {equipamento.nome} (ID: {equipamento.id})\n"
        resultado += f"📅 Data Prevista: {data_formatada}\n"
        resultado += f"🔧 Motivo: {motivo}\n"
        
        if descricao:
            resultado += f"📝 Descrição: {descricao}\n"
        
        return resultado
        
    except Exception as e:
        return f"Erro ao agendar manutenção: {str(e)}"


class AgendarManutencaoTool(BaseTool):
    """
    Ferramenta para agendar novas manutenções para equipamentos.
    Cria registros de manutenção preventiva ou corretiva no sistema.
    """
    
    @property
    def function_declaration(self):
        return agendar_manutencao
    
    def call_chat_display(self) -> str:
        return "📅 Agendando nova manutenção..."
    
    def call_result_display(self, result: str) -> str:
        return result
