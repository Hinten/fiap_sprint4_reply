import importlib
import inspect
import logging
import os
import sys

from src.database.tipos_base.model import Model

logger = logging.getLogger(__name__)


def import_models(sort: bool = False) -> dict[str, type[Model]]:
    """
    Importa todas as classes que herdam de Model na pasta src/database/models.
    
    Tenta primeiro usar o arquivo gerado estaticamente (generated_models_imports.py)
    para melhor performance e determinismo. Se não estiver disponível, faz o
    fallback para importação dinâmica em runtime.
    
    :param sort: bool - Se True, ordena os modelos pela ordem de importação do banco de dados
    :return: dict - Um dicionário com o nome das classes como chave e as classes como valor.
    """
    # Tenta primeiro usar o arquivo gerado estaticamente
    try:
        from src.database.generated_models_imports import import_generated_models
        import_generated_models()
        logger.debug("Using static generated imports for models")
    except (ImportError, AttributeError) as e:
        logger.debug(f"Generated imports not available, falling back to dynamic import: {e}")
        # Fallback para importação dinâmica
        _dynamic_import_models()
    
    # Depois de importar os módulos (estática ou dinamicamente),
    # coleta todas as classes Model que foram registradas
    models = _collect_model_classes()
    
    if sort:
        models = dict(sorted(models.items(), key=lambda item: item[1].__database_import_order__))

    return models


def _dynamic_import_models() -> None:
    """
    Importa dinamicamente todos os módulos de modelo (fallback method).
    
    Esta função é chamada quando o arquivo gerado estaticamente não está disponível.
    """
    models_path = os.path.join(os.path.dirname(__file__), "models")
    
    if not os.path.exists(models_path):
        logger.warning(f"Models directory not found: {models_path}")
        return

    for file in os.listdir(models_path):
        if file.endswith(".py") and file != "__init__.py":
            # Remove o caminho do arquivo e substitui por um ponto
            # para formar o nome do módulo
            # Exemplo: src/database/models/modelo.py -> src.database.models.modelo
            # Isso é necessário para que o import funcione corretamente e o módulo seja encontrado.

            src_path = list(models_path.split(os.sep))
            try:
                src_index = src_path.index('src')
                src_path = '.'.join(src_path[src_index:])
            except ValueError:
                logger.error(f"Could not find 'src' in path: {models_path}")
                continue
                
            module_name = f"{src_path}.{file[:-3]}"
            
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                logger.error(f"Failed to import module {module_name}: {e}")


def _collect_model_classes() -> dict[str, type[Model]]:
    """
    Coleta todas as classes Model que foram importadas.
    
    Esta função varre todos os módulos importados sob src.database.models
    e encontra todas as classes que herdam de Model.
    
    :return: dict - Um dicionário com o nome das classes como chave e as classes como valor.
    """
    models = {}
    models_path = os.path.join(os.path.dirname(__file__), "models")
    
    if not os.path.exists(models_path):
        logger.warning(f"Models directory not found: {models_path}")
        return models
    
    for file in os.listdir(models_path):
        if file.endswith(".py") and file != "__init__.py":
            src_path = list(models_path.split(os.sep))
            try:
                src_index = src_path.index('src')
                src_path = '.'.join(src_path[src_index:])
            except ValueError:
                logger.error(f"Could not find 'src' in path: {models_path}")
                continue
                
            module_name = f"{src_path}.{file[:-3]}"
            
            # Try to get the module if it's already imported
            if module_name in sys.modules:
                module = sys.modules[module_name]
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Model) and obj is not Model:
                        models[name] = obj
    
    return models

def get_model_by_name(name: str) -> type[Model]:
    """
    Retorna uma instância do modelo baseado no nome.
    :param name: Nome do modelo.
    :return: Model - Instância do modelo.
    """
    models = import_models()
    model_class = models.get(name)
    if model_class:
        return model_class
    else:
        raise ValueError(f"Model '{name}' não encontrado.")

def get_model_by_table_name(table_name: str) -> type[Model]:
    """
    Retorna uma instância do modelo baseado no nome da tabela.
    :param table_name: Nome da tabela.
    :return: Model - Instância do modelo.
    """
    models = import_models()
    for model_class in models.values():
        if model_class.__tablename__ == table_name:
            return model_class
    raise ValueError(f"Model com tabela '{table_name}' não encontrado.")

if __name__ == "__main__":
    models = import_models()
    for name, model in models.items():
        print(f"Modelo: {name}, Classe: {model}")