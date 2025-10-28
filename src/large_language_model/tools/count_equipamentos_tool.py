"""
Example tool: Count equipment by company.
This demonstrates how to create a tool that queries the database.
"""
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.equipamento import Equipamento
from src.database.models.empresa import Empresa


def count_equipamentos_por_empresa(empresa_id: int = None) -> str:
    """
    Conta quantos equipamentos estão cadastrados por empresa.
    Se empresa_id for fornecido, retorna apenas para aquela empresa.
    Caso contrário, retorna um resumo de todas as empresas.
    
    :param empresa_id: ID da empresa (opcional). Se não fornecido, conta para todas as empresas.
    :return: String com a contagem de equipamentos por empresa
    """
    try:
        if empresa_id is not None:
            # Buscar empresa específica
            empresa = Empresa.get_from_id(empresa_id)
            if not empresa:
                return f"Empresa com ID {empresa_id} não encontrada."
            
            count = Equipamento.count(empresa_id=empresa_id)
            return f"A empresa '{empresa.nome}' possui {count} equipamento(s) cadastrado(s)."
        else:
            # Listar todas as empresas
            empresas = Empresa.all()
            if not empresas:
                return "Nenhuma empresa cadastrada no sistema."
            
            resultado = "Equipamentos por empresa:\n"
            total = 0
            for empresa in empresas:
                count = Equipamento.count(empresa_id=empresa.id)
                total += count
                resultado += f"  - {empresa.nome}: {count} equipamento(s)\n"
            
            resultado += f"\nTotal geral: {total} equipamento(s)"
            return resultado
            
    except Exception as e:
        return f"Erro ao consultar equipamentos: {str(e)}"


class CountEquipamentosTool(BaseTool):
    """
    Ferramenta para contar equipamentos cadastrados por empresa.
    Útil para verificar a distribuição de equipamentos no sistema.
    """
    
    @property
    def function_declaration(self):
        return count_equipamentos_por_empresa
    
    def call_chat_display(self) -> str:
        return "📊 Contando equipamentos por empresa..."
    
    def call_result_display(self, result: str) -> str:
        return f"✅ {result}"
