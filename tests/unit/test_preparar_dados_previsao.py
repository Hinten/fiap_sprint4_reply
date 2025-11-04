"""
Teste para verificar a função preparar_dados_para_previsao
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.dashboard.machine_learning.manual import preparar_dados_para_previsao


def test_preparar_dados_para_previsao_formato_correto():
    """Testa se a função retorna DataFrame com formato correto."""
    # Arrange
    lux = 15.0
    temp = 14.0
    vibracao = 0.5
    
    # Act
    result = preparar_dados_para_previsao(lux, temp, vibracao)
    
    # Assert
    assert isinstance(result, pd.DataFrame), "Deve retornar um DataFrame"
    assert result.shape == (1, 3), "Deve ter 1 linha e 3 colunas"
    
    # Verifica os nomes das colunas (exatamente como no treinamento)
    expected_columns = ['Lux (x10³)', 'Temperatura (°C)', 'Vibração']
    assert list(result.columns) == expected_columns, f"Colunas devem ser {expected_columns}"
    
    # Verifica os valores
    assert result['Lux (x10³)'].iloc[0] == lux
    assert result['Temperatura (°C)'].iloc[0] == temp
    assert result['Vibração'].iloc[0] == vibracao


def test_preparar_dados_para_previsao_tipos_corretos():
    """Testa se os tipos de dados estão corretos."""
    # Arrange
    lux = 20.5
    temp = 25.3
    vibracao = 1.2
    
    # Act
    result = preparar_dados_para_previsao(lux, temp, vibracao)
    
    # Assert
    assert result['Lux (x10³)'].dtype in [float, 'float64']
    assert result['Temperatura (°C)'].dtype in [float, 'float64']
    assert result['Vibração'].dtype in [float, 'float64']


def test_preparar_dados_para_previsao_valores_zero():
    """Testa com valores zero."""
    # Arrange
    lux = 0.0
    temp = 0.0
    vibracao = 0.0
    
    # Act
    result = preparar_dados_para_previsao(lux, temp, vibracao)
    
    # Assert
    assert result['Lux (x10³)'].iloc[0] == 0.0
    assert result['Temperatura (°C)'].iloc[0] == 0.0
    assert result['Vibração'].iloc[0] == 0.0


def test_preparar_dados_para_previsao_valores_negativos():
    """Testa com valores negativos (caso possível)."""
    # Arrange
    lux = -5.0
    temp = -10.0
    vibracao = -1.0
    
    # Act
    result = preparar_dados_para_previsao(lux, temp, vibracao)
    
    # Assert
    assert result['Lux (x10³)'].iloc[0] == -5.0
    assert result['Temperatura (°C)'].iloc[0] == -10.0
    assert result['Vibração'].iloc[0] == -1.0


def test_preparar_dados_para_previsao_valores_grandes():
    """Testa com valores grandes."""
    # Arrange
    lux = 1000.5
    temp = 100.2
    vibracao = 999.9
    
    # Act
    result = preparar_dados_para_previsao(lux, temp, vibracao)
    
    # Assert
    assert result['Lux (x10³)'].iloc[0] == 1000.5
    assert result['Temperatura (°C)'].iloc[0] == 100.2
    assert result['Vibração'].iloc[0] == 999.9
