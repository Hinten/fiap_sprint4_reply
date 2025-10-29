"""
Tools package for extending LLM capabilities.

Tools são funções que o modelo de linguagem pode chamar para obter informações
ou executar ações no sistema. 

Para criar uma nova tool:
1. Crie um arquivo .py neste diretório
2. Crie uma classe que herda de BaseTool
3. Implemente os métodos abstratos obrigatórios
4. A tool será automaticamente descoberta e registrada

Exemplo:
    from datetime import datetime
    from src.large_language_model.tipos_base.base_tools import BaseTool

    def minha_funcao() -> str:
        '''
        Descrição da função que será mostrada ao modelo.
        :return: Resultado da função.
        '''
        return "Resultado"

    class MinhaTool(BaseTool):
        @property
        def function_declaration(self):
            return minha_funcao

        def call_chat_display(self) -> str:
            return "Executando minha tool..."

        def call_result_display(self, result: str) -> str:
            return f"Resultado: {result}"
"""
