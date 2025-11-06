"""
Tool for listing all installed equipment in the system.
Provides information about equipment including ID, name, model, location, and installation date.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.equipamento import Equipamento


def listar_equipamentos() -> str:
    """
    Lista todos os equipamentos instalados no sistema.
    
    Retorna informações detalhadas sobre cada equipamento cadastrado,
    incluindo ID, nome, modelo, localização e data de instalação.
    Útil para verificar quais equipamentos estão monitorados.
    
    :return: String formatada com a lista de equipamentos e suas informações
    """
    try:
        equipamentos = Equipamento.all()
        
        if not equipamentos:
            return "Nenhum equipamento cadastrado no sistema."
        
        resultado = f"Total de {len(equipamentos)} equipamento(s) cadastrado(s):\n\n"
        
        for equip in equipamentos:
            resultado += f"📦 ID: {equip.id}\n"
            resultado += f"   Nome: {equip.nome}\n"
            
            if equip.modelo:
                resultado += f"   Modelo: {equip.modelo}\n"
            
            if equip.localizacao:
                resultado += f"   Localização: {equip.localizacao}\n"
            
            if equip.data_instalacao:
                data_formatada = equip.data_instalacao.strftime('%d/%m/%Y')
                resultado += f"   Data de Instalação: {data_formatada}\n"
            
            # Count associated sensors
            num_sensores = len(equip.sensores) if equip.sensores else 0
            resultado += f"   Sensores: {num_sensores}\n"
            
            if equip.descricao:
                resultado += f"   Descrição: {equip.descricao}\n"
            
            resultado += "\n"
        
        return resultado.strip()
        
    except Exception as e:
        return f"Erro ao listar equipamentos: {str(e)}"


class ListarEquipamentosTool(BaseTool):
    """
    Ferramenta para listar todos os equipamentos cadastrados no sistema.
    Retorna informações detalhadas de cada equipamento monitorado.
    """
    
    @property
    def function_declaration(self):
        return listar_equipamentos
    
    def call_chat_display(self) -> str:
        return "📦 Listando equipamentos cadastrados..."
    
    def call_result_display(self, result: str) -> str:
        return f"✅ Equipamentos:\n{result}"
