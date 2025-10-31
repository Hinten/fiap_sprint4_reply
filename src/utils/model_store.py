"""
Utilitário para gerenciar modelos de machine learning salvos.

Este módulo fornece funcionalidades para:
- Salvar modelos treinados com metadados
- Listar modelos disponíveis
- Carregar modelos salvos
- Manter registro persistente em JSON
"""

import joblib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading


# Lock para operações thread-safe no registry
_registry_lock = threading.Lock()

# Diretório base para modelos
MODELS_DIR = Path(__file__).parent.parent / "machine_learning" / "modelos_salvos"
REGISTRY_FILE = MODELS_DIR / "registry.json"

# Garante que o diretório existe
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def _load_registry() -> Dict[str, Any]:
    """
    Carrega o registro de modelos do arquivo JSON.
    
    Returns:
        Dicionário com informações dos modelos registrados
    """
    with _registry_lock:
        if REGISTRY_FILE.exists():
            try:
                return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                # Se houver erro na leitura, retorna dict vazio
                return {}
        return {}


def _save_registry(registry: Dict[str, Any]) -> None:
    """
    Salva o registro de modelos no arquivo JSON de forma atômica.
    
    Args:
        registry: Dicionário com informações dos modelos
    """
    with _registry_lock:
        # Salva em arquivo temporário primeiro para garantir atomicidade
        tmp_file = REGISTRY_FILE.with_suffix(".tmp")
        tmp_file.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        # Substitui o arquivo original atomicamente
        tmp_file.replace(REGISTRY_FILE)


def save_model(
    model_obj: Any,
    name: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Salva um modelo com seus metadados no registro.
    
    Args:
        model_obj: Objeto do modelo treinado
        name: Nome único para o modelo
        metadata: Dicionário com metadados opcionais (métricas, tipo, etc.)
        
    Raises:
        ValueError: Se o nome já existir no registro
    """
    if metadata is None:
        metadata = {}
    
    # Verifica se o nome já existe
    registry = _load_registry()
    if name in registry:
        raise ValueError(f"Modelo '{name}' já existe no registro. Use outro nome.")
    
    # Define o caminho do arquivo
    filename = MODELS_DIR / f"{name}.pkl"
    
    # Salva o modelo usando joblib
    joblib.dump(model_obj, filename)
    
    # Atualiza o registro
    registry[name] = {
        "path": str(filename.relative_to(MODELS_DIR.parent)),
        "metadata": metadata,
        "saved_at": datetime.utcnow().isoformat()
    }
    
    _save_registry(registry)


def list_models() -> Dict[str, Any]:
    """
    Lista todos os modelos registrados.
    
    Returns:
        Dicionário com informações de todos os modelos registrados
    """
    return _load_registry()


def load_model(name: str) -> Any:
    """
    Carrega um modelo salvo pelo nome.
    
    Args:
        name: Nome do modelo a ser carregado
        
    Returns:
        Objeto do modelo carregado
        
    Raises:
        FileNotFoundError: Se o modelo não existir no registro
        IOError: Se houver erro ao carregar o arquivo
    """
    registry = _load_registry()
    entry = registry.get(name)
    
    if not entry:
        raise FileNotFoundError(f"Modelo '{name}' não encontrado no registro.")
    
    # Constrói o caminho completo
    model_path = MODELS_DIR.parent / entry["path"]
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Arquivo do modelo '{name}' não encontrado em {model_path}"
        )
    
    return joblib.load(model_path)


def delete_model(name: str) -> None:
    """
    Remove um modelo do registro e deleta o arquivo.
    
    Args:
        name: Nome do modelo a ser removido
        
    Raises:
        FileNotFoundError: Se o modelo não existir no registro
    """
    registry = _load_registry()
    entry = registry.get(name)
    
    if not entry:
        raise FileNotFoundError(f"Modelo '{name}' não encontrado no registro.")
    
    # Remove o arquivo se existir
    model_path = MODELS_DIR.parent / entry["path"]
    if model_path.exists():
        model_path.unlink()
    
    # Remove do registro
    del registry[name]
    _save_registry(registry)


def get_model_metadata(name: str) -> Dict[str, Any]:
    """
    Obtém os metadados de um modelo específico.
    
    Args:
        name: Nome do modelo
        
    Returns:
        Dicionário com os metadados do modelo
        
    Raises:
        KeyError: Se o modelo não existir no registro
    """
    registry = _load_registry()
    if name not in registry:
        raise KeyError(f"Modelo '{name}' não encontrado no registro.")
    
    return registry[name]


def get_models_summary() -> List[Dict[str, Any]]:
    """
    Retorna um resumo de todos os modelos em formato de lista.
    
    Returns:
        Lista de dicionários com informações resumidas de cada modelo
    """
    registry = _load_registry()
    summary = []
    
    for name, info in registry.items():
        model_info = {
            "name": name,
            "saved_at": info.get("saved_at", "Unknown"),
            **info.get("metadata", {})
        }
        summary.append(model_info)
    
    return summary
