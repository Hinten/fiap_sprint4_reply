import importlib
import inspect
import logging
import os
import sys

from src.large_language_model.tipos_base.base_tools import BaseTool

logger = logging.getLogger(__name__)


def import_tools(sort: bool = False) -> dict[str, type[BaseTool]]:
    """
    Importa todas as classes que herdam de BaseTool na pasta src/large_language_model/tools.
    
    Tenta primeiro usar o arquivo gerado estaticamente (generated_tools_imports.py)
    para melhor performance e determinismo. Se não estiver disponível, faz o
    fallback para importação dinâmica em runtime.
    
    :param sort: bool - Se True, ordena as ferramentas por nome
    :return: dict - Um dicionário com o nome das classes como chave e as classes como valor.
    """
    # Tenta primeiro usar o arquivo gerado estaticamente
    try:
        from src.large_language_model.generated_tools_imports import import_generated_tools
        import_generated_tools()
        logger.debug("Using static generated imports for tools")
    except (ImportError, AttributeError) as e:
        logger.debug(f"Generated imports not available, falling back to dynamic import: {e}")
        # Fallback para importação dinâmica
        _dynamic_import_tools()
    
    # Depois de importar os módulos (estática ou dinamicamente),
    # coleta todas as classes BaseTool que foram registradas
    tools = _collect_tool_classes()
    
    if sort:
        tools = dict(sorted(tools.items(), key=lambda item: item[0].lower()))

    return tools


def _dynamic_import_tools() -> None:
    """
    Importa dinamicamente todos os módulos de ferramenta (fallback method).
    
    Esta função é chamada quando o arquivo gerado estaticamente não está disponível.
    """
    tools_path = os.path.join(os.path.dirname(__file__), "tools")
    
    if not os.path.exists(tools_path):
        logger.warning(f"Tools directory not found: {tools_path}")
        return

    for file in os.listdir(tools_path):
        if file.endswith(".py") and file != "__init__.py":
            # Remove o caminho do arquivo e substitui por um ponto
            # para formar o nome do módulo
            # Exemplo: src/large_language_model/tools/exemplo.py -> src.large_language_model.tools.exemplo
            # Isso é necessário para que o import funcione corretamente e o módulo seja encontrado.

            src_path = list(tools_path.split(os.sep))
            try:
                src_index = src_path.index('src')
                src_path = '.'.join(src_path[src_index:])
            except ValueError:
                logger.error(f"Could not find 'src' in path: {tools_path}")
                continue
                
            module_name = f"{src_path}.{file[:-3]}"
            
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                logger.error(f"Failed to import module {module_name}: {e}")


def _collect_tool_classes() -> dict[str, type[BaseTool]]:
    """
    Coleta todas as classes BaseTool que foram importadas.
    
    Esta função varre todos os módulos importados sob src.large_language_model.tools
    e encontra todas as classes que herdam de BaseTool.
    
    :return: dict - Um dicionário com o nome das classes como chave e as classes como valor.
    """
    tools = {}
    tools_path = os.path.join(os.path.dirname(__file__), "tools")
    
    if not os.path.exists(tools_path):
        logger.warning(f"Tools directory not found: {tools_path}")
        return tools
    
    for file in os.listdir(tools_path):
        if file.endswith(".py") and file != "__init__.py":
            src_path = list(tools_path.split(os.sep))
            try:
                src_index = src_path.index('src')
                src_path = '.'.join(src_path[src_index:])
            except ValueError:
                logger.error(f"Could not find 'src' in path: {tools_path}")
                continue
                
            module_name = f"{src_path}.{file[:-3]}"
            
            # Try to get the module if it's already imported
            if module_name in sys.modules:
                module = sys.modules[module_name]
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseTool) and obj is not BaseTool:
                        tools[name] = obj
    
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
