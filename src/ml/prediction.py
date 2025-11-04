"""
Reusable machine learning prediction utilities.

This module provides functions for loading ML models and making predictions
for equipment maintenance. It can be used by both the dashboard and LLM tools.
"""

import os
import joblib
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from src.utils.model_store import list_models, load_model as load_model_from_registry


def preparar_dados_para_previsao(lux: float, temp: float, vibracao: float) -> pd.DataFrame:
    """
    Prepara os dados de entrada no formato correto esperado pelos modelos PyCaret.
    
    Os modelos treinados pelo PyCaret esperam um DataFrame com os nomes de colunas
    exatamente como foram usados no treinamento: 'Lux (x10³)', 'Temperatura (°C)', 'Vibração'.
    
    Args:
        lux: Valor da intensidade luminosa
        temp: Valor da temperatura
        vibracao: Valor da vibração
        
    Returns:
        DataFrame com uma linha e colunas nomeadas corretamente
    """
    # Cria DataFrame com os nomes de colunas corretos usados no treinamento
    dados_df = pd.DataFrame({
        'Lux (x10³)': [lux],
        'Temperatura (°C)': [temp],
        'Vibração': [vibracao]
    })
    
    return dados_df


def carregar_modelo_do_registry(nome_modelo: Optional[str] = None) -> Tuple[Any, Dict[str, Any]]:
    """
    Carrega um modelo do registry de modelos.
    
    Args:
        nome_modelo: Nome do modelo a carregar. Se None, carrega o primeiro disponível.
        
    Returns:
        Tupla (modelo, metadados) onde metadados contém informações sobre o modelo
        
    Raises:
        FileNotFoundError: Se não houver modelos no registry
    """
    registry = list_models()
    
    if not registry:
        raise FileNotFoundError("Nenhum modelo encontrado no registry.")
    
    if nome_modelo is None:
        # Pega o primeiro modelo disponível
        nome_modelo = next(iter(registry.keys()))
    
    if nome_modelo not in registry:
        raise FileNotFoundError(f"Modelo '{nome_modelo}' não encontrado no registry.")
    
    modelo = load_model_from_registry(nome_modelo)
    metadados = registry[nome_modelo]
    
    return modelo, metadados


def carregar_modelo_legado(caminho_modelo: Optional[str] = None) -> Any:
    """
    Carrega um modelo usando o método legado de arquivo.
    
    Args:
        caminho_modelo: Caminho para o arquivo do modelo. Se None, tenta carregar
                       o modelo padrão (preferindo modelos com 3 features)
        
    Returns:
        Modelo carregado
        
    Raises:
        FileNotFoundError: Se o modelo não for encontrado
    """
    if caminho_modelo is None:
        # Tenta múltiplos caminhos padrão
        # Preferimos modelos com 3 features (modelos_salvos) que funcionam com nosso input
        base_dir = Path(__file__).parent.parent.parent
        possiveis_caminhos = [
            # Primeiro, tenta modelos com 3 features (compatíveis com input simples)
            base_dir / "src" / "machine_learning" / "modelos_salvos" / "random_forest.joblib",
            base_dir / "src" / "machine_learning" / "modelos_salvos" / "logistic_regression.joblib",
            base_dir / "src" / "machine_learning" / "modelos_salvos" / "kneighbors.joblib",
            # Não usar DecTree_d5.pkl pois tem 4 features
            # base_dir / "src" / "machine_learning" / "modelos_salvos" / "DecTree_d5.pkl",
            base_dir / "assets" / "modelos_salvos" / "random_forest.joblib",
        ]
        
        for caminho in possiveis_caminhos:
            if caminho.exists():
                caminho_modelo = str(caminho)
                break
        else:
            raise FileNotFoundError(
                "Modelo padrão não encontrado. Execute o treinamento de modelos "
                "ou especifique um caminho válido."
            )
    
    if not os.path.exists(caminho_modelo):
        raise FileNotFoundError(f"Modelo não encontrado em: {caminho_modelo}")
    
    return joblib.load(caminho_modelo)


def carregar_modelo(nome_ou_caminho: Optional[str] = None, 
                   usar_registry: bool = True) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """
    Carrega um modelo de ML, tentando primeiro o registry e depois o método legado.
    
    Args:
        nome_ou_caminho: Nome do modelo no registry ou caminho para arquivo
        usar_registry: Se True, tenta carregar do registry primeiro
        
    Returns:
        Tupla (modelo, metadados) onde metadados pode ser None se usar método legado
    """
    if usar_registry:
        try:
            return carregar_modelo_do_registry(nome_ou_caminho)
        except (FileNotFoundError, Exception):
            # Se falhar, tenta método legado
            pass
    
    # Método legado
    modelo = carregar_modelo_legado(nome_ou_caminho)
    return modelo, None


def realizar_previsao(
    modelo: Any,
    lux: float,
    temp: float,
    vibracao: float
) -> Dict[str, Any]:
    """
    Realiza predição de manutenção usando um modelo já carregado.
    
    Args:
        modelo: Modelo de ML já carregado
        lux: Valor da intensidade luminosa
        temp: Valor da temperatura
        vibracao: Valor da vibração
        
    Returns:
        Dicionário com:
            - predicao: 0 (sem manutenção) ou 1 (com manutenção)
            - probabilidade_manutencao: Probabilidade de necessitar manutenção (0-1)
            - probabilidade_sem_manutencao: Probabilidade de não necessitar (0-1)
            - tem_proba: Se o modelo suporta predict_proba
    """
    # Prepara os dados
    dados_para_prever = preparar_dados_para_previsao(lux, temp, vibracao)
    
    # Faz a previsão
    resultado_numerico = modelo.predict(dados_para_prever)[0]
    
    # Calcula probabilidades se o modelo suportar
    tem_proba = hasattr(modelo, 'predict_proba')
    if tem_proba:
        probabilidades = modelo.predict_proba(dados_para_prever)[0]
        prob_sem_manutencao = float(probabilidades[0])
        prob_manutencao = float(probabilidades[1])
    else:
        # Se não tiver predict_proba, usa valores binários
        prob_sem_manutencao = 0.0 if resultado_numerico == 1 else 1.0
        prob_manutencao = 1.0 if resultado_numerico == 1 else 0.0
    
    return {
        'predicao': int(resultado_numerico),
        'probabilidade_manutencao': prob_manutencao,
        'probabilidade_sem_manutencao': prob_sem_manutencao,
        'tem_proba': tem_proba,
        'dados_entrada': {
            'lux': lux,
            'temperatura': temp,
            'vibracao': vibracao
        }
    }


def carregar_modelo_e_realizar_previsao(
    lux: float,
    temp: float,
    vibracao: float,
    nome_ou_caminho_modelo: Optional[str] = None,
    usar_registry: bool = True
) -> Dict[str, Any]:
    """
    Função completa que carrega o modelo e realiza a predição.
    
    Esta é a função principal que deve ser usada pelo dashboard e ferramentas LLM.
    
    Args:
        lux: Valor da intensidade luminosa
        temp: Valor da temperatura
        vibracao: Valor da vibração
        nome_ou_caminho_modelo: Nome do modelo no registry ou caminho para arquivo
        usar_registry: Se True, tenta carregar do registry primeiro
        
    Returns:
        Dicionário com resultados da predição (ver realizar_previsao)
        
    Raises:
        FileNotFoundError: Se nenhum modelo for encontrado
        Exception: Outros erros durante carregamento ou predição
    """
    # Carrega o modelo
    modelo, metadados = carregar_modelo(nome_ou_caminho_modelo, usar_registry)
    
    # Realiza a predição
    resultado = realizar_previsao(modelo, lux, temp, vibracao)
    
    # Adiciona metadados se disponível
    if metadados:
        resultado['modelo_info'] = metadados
    
    return resultado


def obter_modelos_disponiveis() -> Dict[str, Any]:
    """
    Retorna informações sobre modelos disponíveis no registry e método legado.
    
    Returns:
        Dicionário com informações dos modelos disponíveis
    """
    resultado = {
        'registry': [],
        'legado': []
    }
    
    # Verifica registry
    try:
        registry = list_models()
        resultado['registry'] = [
            {
                'nome': nome,
                'info': info
            }
            for nome, info in registry.items()
        ]
    except Exception:
        pass
    
    # Verifica modelos legados
    base_dir = Path(__file__).parent.parent.parent
    possiveis_pastas = [
        base_dir / "assets" / "modelos_otimizados_salvos",
        base_dir / "assets" / "modelos_salvos",
        base_dir / "src" / "machine_learning" / "modelos_otimizados_salvos",
        base_dir / "src" / "machine_learning" / "modelos_salvos",
    ]
    
    for pasta in possiveis_pastas:
        if pasta.exists():
            for arquivo in pasta.glob("*.pkl"):
                resultado['legado'].append({
                    'nome': arquivo.stem,
                    'caminho': str(arquivo)
                })
            for arquivo in pasta.glob("*.joblib"):
                resultado['legado'].append({
                    'nome': arquivo.stem,
                    'caminho': str(arquivo)
                })
    
    return resultado
