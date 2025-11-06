"""
Unit tests for the ML prediction module.
Tests the reusable prediction functions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np

from src.ml.prediction import (
    preparar_dados_para_previsao,
    carregar_modelo_legado,
    carregar_modelo_do_registry,
    carregar_modelo,
    realizar_previsao,
    carregar_modelo_e_realizar_previsao,
    obter_modelos_disponiveis
)


class TestPrepararDadosParaPrevisao:
    """Tests for data preparation function."""
    
    def test_prepara_dados_formato_correto(self):
        """Test that data is prepared in the correct format."""
        df = preparar_dados_para_previsao(lux=15.0, temp=25.0, vibracao=0.5)
        
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (1, 3)
        assert 'Lux (x10³)' in df.columns
        assert 'Temperatura (°C)' in df.columns
        assert 'Vibração' in df.columns
        assert df['Lux (x10³)'].iloc[0] == 15.0
        assert df['Temperatura (°C)'].iloc[0] == 25.0
        assert df['Vibração'].iloc[0] == 0.5
    
    def test_prepara_dados_diferentes_valores(self):
        """Test with different input values."""
        df = preparar_dados_para_previsao(lux=100.0, temp=-10.0, vibracao=2.5)
        
        assert df['Lux (x10³)'].iloc[0] == 100.0
        assert df['Temperatura (°C)'].iloc[0] == -10.0
        assert df['Vibração'].iloc[0] == 2.5


class TestCarregarModelo:
    """Tests for model loading functions."""
    
    @patch('src.ml.prediction.os.path.exists', return_value=False)
    def test_carregar_modelo_legado_nao_encontrado(self, mock_exists):
        """Test loading model when file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Modelo não encontrado"):
            carregar_modelo_legado("/path/to/nonexistent/model.pkl")
    
    @patch('src.ml.prediction.joblib.load')
    @patch('src.ml.prediction.os.path.exists', return_value=True)
    def test_carregar_modelo_legado_sucesso(self, mock_exists, mock_joblib_load):
        """Test successful model loading."""
        mock_model = Mock()
        mock_joblib_load.return_value = mock_model
        
        model = carregar_modelo_legado("/path/to/model.pkl")
        assert model == mock_model
        mock_joblib_load.assert_called_once_with("/path/to/model.pkl")
    
    @patch('src.ml.prediction.list_models')
    def test_carregar_modelo_registry_vazio(self, mock_list_models):
        """Test loading from empty registry."""
        mock_list_models.return_value = {}
        
        with pytest.raises(FileNotFoundError):
            carregar_modelo_do_registry()
    
    @patch('src.ml.prediction.load_model_from_registry')
    @patch('src.ml.prediction.list_models')
    def test_carregar_modelo_registry_sucesso(self, mock_list_models, mock_load_model):
        """Test successful model loading from registry."""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        mock_list_models.return_value = {
            'test_model': {
                'path': 'test/path',
                'metadata': {'accuracy': 0.95}
            }
        }
        
        model, metadata = carregar_modelo_do_registry('test_model')
        assert model == mock_model
        assert 'path' in metadata


class TestRealizarPrevisao:
    """Tests for prediction execution."""
    
    def test_realizar_previsao_com_proba(self):
        """Test prediction with a model that supports predict_proba."""
        mock_model = Mock()
        mock_model.predict.return_value = np.array([1])
        mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])
        
        resultado = realizar_previsao(mock_model, lux=15.0, temp=25.0, vibracao=0.5)
        
        assert resultado['predicao'] == 1
        assert resultado['probabilidade_manutencao'] == 0.7
        assert resultado['probabilidade_sem_manutencao'] == 0.3
        assert resultado['tem_proba'] is True
        assert resultado['dados_entrada']['lux'] == 15.0
        assert resultado['dados_entrada']['temperatura'] == 25.0
        assert resultado['dados_entrada']['vibracao'] == 0.5
    
    def test_realizar_previsao_sem_proba(self):
        """Test prediction with a model that doesn't support predict_proba."""
        mock_model = Mock()
        mock_model.predict.return_value = np.array([0])
        del mock_model.predict_proba  # Remove predict_proba attribute
        
        resultado = realizar_previsao(mock_model, lux=10.0, temp=20.0, vibracao=0.3)
        
        assert resultado['predicao'] == 0
        assert resultado['probabilidade_manutencao'] == 0.0
        assert resultado['probabilidade_sem_manutencao'] == 1.0
        assert resultado['tem_proba'] is False


class TestCarregarModeloERealizarPrevisao:
    """Tests for the complete workflow function."""
    
    @patch('src.ml.prediction.realizar_previsao')
    @patch('src.ml.prediction.carregar_modelo')
    def test_workflow_completo(self, mock_carregar, mock_realizar):
        """Test complete prediction workflow."""
        mock_model = Mock()
        mock_carregar.return_value = (mock_model, None)
        mock_realizar.return_value = {
            'predicao': 1,
            'probabilidade_manutencao': 0.8,
            'probabilidade_sem_manutencao': 0.2,
            'tem_proba': True,
            'dados_entrada': {'lux': 15.0, 'temperatura': 25.0, 'vibracao': 0.5}
        }
        
        resultado = carregar_modelo_e_realizar_previsao(
            lux=15.0, temp=25.0, vibracao=0.5
        )
        
        assert resultado['predicao'] == 1
        assert resultado['probabilidade_manutencao'] == 0.8
        mock_carregar.assert_called_once()
        mock_realizar.assert_called_once_with(mock_model, 15.0, 25.0, 0.5)


class TestObterModelosDisponiveis:
    """Tests for listing available models."""
    
    @patch('src.ml.prediction.list_models')
    def test_obter_modelos_registry(self, mock_list_models):
        """Test getting models from registry."""
        mock_list_models.return_value = {
            'model1': {'path': 'path1'},
            'model2': {'path': 'path2'}
        }
        
        modelos = obter_modelos_disponiveis()
        
        assert len(modelos['registry']) == 2
        assert modelos['registry'][0]['nome'] == 'model1'
        assert modelos['registry'][1]['nome'] == 'model2'
    
    @patch('src.ml.prediction.list_models')
    def test_obter_modelos_vazio(self, mock_list_models):
        """Test when no models are available."""
        mock_list_models.side_effect = Exception("No registry")
        
        modelos = obter_modelos_disponiveis()
        
        # Should still return a structure even if registry fails
        assert 'registry' in modelos
        assert 'legado' in modelos
