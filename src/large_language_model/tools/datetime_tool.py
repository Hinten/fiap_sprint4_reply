from datetime import datetime

from src.large_language_model.tipos_base.base_tools import BaseTool


def get_current_time() -> str:
    """
    Retorna a data e hora atual no formato ISO 8601.
    Esta ferramenta pode ser usada para obter o timestamp atual do sistema.
    :return: String representando a data e hora atual no formato ISO 8601.
    """
    return datetime.now().isoformat()

class DateTimeTool(BaseTool):
    """
    Ferramenta para obter a data e hora atual do sistema.
    Útil para contextualizar análises de dados de sensores e eventos.
    """

    @property
    def function_declaration(self):
        return get_current_time

    def execute(self, *args, **kwargs) -> str:
        return get_current_time()

    def call_chat_display(self) -> str:
        return "🕐 Obtendo data e hora atual do sistema..."

    def call_result_display(self, result: str) -> str:
        return f"✅ Data e hora atual: {result}"
