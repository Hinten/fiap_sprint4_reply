from abc import ABC, abstractmethod
from typing import Callable, Any
from google.genai import types
from datetime import datetime

class BaseTool(ABC):
    """
    Classe base para ferramentas que podem ser utilizadas em um modelo de linguagem generativa.
    """

    @property
    @abstractmethod
    def function_declaration(self) -> Callable[..., Any]:
        """
        A declaração de função que define a interface da ferramenta.
        Deve ser implementada pelas subclasses utilizando obrigatoriamente o decorator @property para fornecer a assinatura da função.
        :return: Um callable que representa a declaração da função.
        """
        pass

    def as_declaration(self) -> types.FunctionDeclaration:
        """
        Retorna a declaração da função como um objeto FunctionDeclaration do Google GenAI.
        :return: types.FunctionDeclaration
        """
        return types.FunctionDeclaration.from_callable_with_api_option(callable=self.function_declaration)

    def __init__(self):

        if not self.function_declaration.__doc__ or not self.function_declaration.__doc__.strip():
            raise ValueError("Function declaration must have a docstring.")

    @property
    def function_name(self) -> str:
        """
        O nome da função que esta ferramenta representa.
        :return: O nome da função.
        """
        return self.function_declaration.__name__


    def execute(self, *args, **kwargs) -> Any:
        """
        Executa a ferramenta com os argumentos fornecidos.
        :param args: Argumentos posicionais para a ferramenta.
        :param kwargs: Argumentos nomeados para a ferramenta.
        :return: O resultado da execução da ferramenta.
        """
        return self.function_declaration(*args, **kwargs)

    def get_result_as_part(self, result: Any) -> types.Part:
        return types.Part.from_function_response(
            name=self.function_name,
            response={
                    'output': str(result),
                }
        )

    @abstractmethod
    def call_chat_display(self) -> str:
        """
        Exibe uma mensagem de chat informando que a ferramenta está sendo chamada.
        """
        pass

    @abstractmethod
    def call_result_display(self, result: Any) -> Any:
        """
        Exibe uma mensagem de chat informando o resultado da chamada da ferramenta.
        """
        pass
