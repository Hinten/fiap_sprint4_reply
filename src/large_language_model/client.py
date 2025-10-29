from google import genai
from google.genai import types, chats
import os
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.large_language_model.system_instructions import SYSTEM_INSTRUCTIONS
from src.large_language_model.dynamic_tools import import_tools
from enum import StrEnum

class AvailableGenerativeModels(StrEnum):
    """
    Enum para os modelos de linguagem generativa disponíveis.
    """
    GEMINI_2_0_FLASH = 'gemini-2.0-flash'
    GEMINI_2_0_FLASH_LITE = 'gemini-2.0-flash-lite'

    def __str__(self):

        match self:
            case AvailableGenerativeModels.GEMINI_2_0_FLASH:
                return "Gemini 2.0 Flash"
            case AvailableGenerativeModels.GEMINI_2_0_FLASH_LITE:
                return "Gemini 2.0 Flash Lite"
            case _:
                return self.value


#https://github.com/googleapis/python-genai
#https://ai.google.dev/gemini-api/docs/text-generation?hl=pt-br
class GenerativeModelClient:
    """
    Cliente para interação com modelos de linguagem generativa do Google Gemini.
    
    Este cliente gerencia:
    - Conexão com a API do Google Gemini
    - Registro e disponibilização de ferramentas (tools) para o modelo
    - Criação e configuração de sessões de chat
    """

    def __init__(self, api_key: str or None= None, generative_model: AvailableGenerativeModels or None = None):
        """
        Inicializa o cliente do modelo generativo.
        
        :param api_key: Chave de API do Google Gemini. Se não fornecida, usa variável de ambiente GEMINI_API.
        :param generative_model: Modelo a ser utilizado. Padrão: GEMINI_2_0_FLASH.
        """
        api_key = api_key or os.getenv("GEMINI_API")

        if not api_key:
            raise ValueError("API key must be provided either as an argument or through the GEMINI_API environment variable.")

        self.client:genai.Client = genai.Client(api_key=api_key)
        self.generative_model:AvailableGenerativeModels = generative_model or AvailableGenerativeModels.GEMINI_2_0_FLASH

        tools = import_tools(sort=True)

        self.tool_list: list[BaseTool] = [tool() for tool in tools.values()]


    def _get_function_declarations(self) -> list[types.FunctionDeclaration]:
        """
        Retorna uma lista de declarações de função para as ferramentas disponíveis.
        :return: Lista de FunctionDeclaration.
        """

        return [tool.as_declaration() for tool in self.tool_list]

    def get_tool(self, tool_name: str) -> BaseTool:
        """
        Retorna uma instância da ferramenta com o nome especificado.
        :param tool_name: Nome da ferramenta a ser retornada.
        :return: Instância da ferramenta correspondente.
        """
        for tool in self.tool_list:
            if tool.function_declaration.__name__ == tool_name:
                return tool
        raise ValueError(f"Tool '{tool_name}' not found.")

    def get_chat(self, generative_model: AvailableGenerativeModels or None = None) -> chats.Chat:
        """
        Inicializa o modelo de linguagem generativa com o nome especificado.

        :param generative_model: Nome do modelo de linguagem a ser inicializado.
        :return: Instância do modelo de linguagem generativa.
        """

        self.generative_model = generative_model or self.generative_model

        return self.client.chats.create(
            model=self.generative_model,
            config=types.GenerateContentConfig(
                # Registra as ferramentas disponíveis para o modelo
                tools=[
                    types.Tool(
                        function_declarations=[

                        ] + self._get_function_declarations(),
                    )
                ],
                system_instruction=SYSTEM_INSTRUCTIONS
            )
        )


if __name__ == "__main__":
    instance = GenerativeModelClient()

    # Exemplo de uso:
    # chat = instance.get_chat()
    # response = chat.send_message("Olá, como você está?")
    # print(response.text)
