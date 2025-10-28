import importlib
import inspect
import os

from src.large_language_model.tipos_base.base_tools import BaseTool

def import_tools(sort: bool = False) -> dict[str, type[BaseTool]]:
    """
    Importa dinamicamente todas as classes que herdam de BaseTool
    na pasta src/large_language_model/tools.
    :param sort: Se True, ordena as ferramentas por nome.
    :return: dict - Um dicionário com o nome das classes como chave e as classes como valor.
    """
    tools = {}
    tools_path = os.path.join(os.path.dirname(__file__), "tools")

    for file in os.listdir(tools_path):
        if file.endswith(".py") and file != "__init__.py":

            # Remove o caminho do arquivo e substitui por um ponto
            # para formar o nome do módulo
            # Exemplo: src/large_language_model/tools/exemplo.py -> src.large_language_model.tools.exemplo
            src_path = list(tools_path.split(os.sep))
            src_path = src_path[src_path.index('src'):]
            src_path = '.'.join(src_path)
            module_name = f"{src_path}.{file[:-3]}"
            # logging.debug(f"Importando módulo: {module_name}")

            module = importlib.import_module(module_name)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    # logging.debug(f"Encontrada classe ferramenta: {name}")
                    tools[name] = obj

    if sort:
        tools = dict(sorted(tools.items(), key=lambda item: item[0].lower()))

    return tools

def get_tool_by_name(name: str) -> type[BaseTool]:
    """
    Retorna uma instância da ferramenta baseada no nome.
    :param name: Nome da ferramenta.
    :return: BaseTool - Instância da ferramenta.
    """
    tools = import_tools()
    tool_class = tools.get(name)
    if tool_class:
        return tool_class
    else:
        raise ValueError(f"Tool '{name}' não encontrada.")
