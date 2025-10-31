"""
Teste de integração para o workflow de modelos.

Testa o fluxo completo:
1. Salvar modelos usando model_store
2. Listar modelos salvos
3. Carregar modelos para previsão
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.utils.model_store import (
    save_model,
    list_models,
    load_model,
    get_models_summary,
    MODELS_DIR
)


class SimpleDummyClassifier:
    """Classificador simples para testes de integração."""
    
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.classes_ = [0, 1]
    
    def predict(self, X):
        """Predição simples baseada em média dos features."""
        predictions = []
        for row in X:
            mean_val = np.mean(row)
            predictions.append(1 if mean_val > self.threshold else 0)
        return np.array(predictions)
    
    def predict_proba(self, X):
        """Retorna probabilidades consistentes com predict."""
        probas = []
        for row in X:
            mean_val = np.mean(row)
            # Se mean_val > threshold, classe 1; senão classe 0
            if mean_val > self.threshold:
                # Calcula distância do threshold (normalizada)
                distance = min((mean_val - self.threshold) / max(self.threshold, 1), 1)
                prob_1 = 0.5 + distance * 0.5  # Entre 0.5 e 1.0
                prob_0 = 1 - prob_1
            else:
                # Calcula distância do threshold (normalizada)
                distance = min((self.threshold - mean_val) / max(self.threshold, 1), 1)
                prob_0 = 0.5 + distance * 0.5  # Entre 0.5 e 1.0
                prob_1 = 1 - prob_0
            probas.append([prob_0, prob_1])
        return np.array(probas)


@pytest.fixture
def temp_models_dir(monkeypatch):
    """Cria diretório temporário para modelos durante testes."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / "modelos_salvos"
    temp_path.mkdir(parents=True, exist_ok=True)
    
    # Monkey patch das constantes do módulo
    monkeypatch.setattr('src.utils.model_store.MODELS_DIR', temp_path)
    monkeypatch.setattr('src.utils.model_store.REGISTRY_FILE', temp_path / "registry.json")
    
    yield temp_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestModelWorkflowIntegration:
    """Testes de integração do workflow de modelos."""
    
    def test_complete_model_workflow(self, temp_models_dir):
        """Testa o fluxo completo de salvar, listar e usar modelos."""
        
        # 1. Cria e salva múltiplos modelos simulando diferentes algoritmos
        models_config = [
            ("random_forest_v1", 0.3, {"accuracy": 0.92, "model_type": "RandomForest"}),
            ("logistic_reg_v1", 0.5, {"accuracy": 0.88, "model_type": "LogisticRegression"}),
            ("svm_v1", 0.4, {"accuracy": 0.90, "model_type": "SVM"}),
        ]
        
        for name, threshold, metadata in models_config:
            model = SimpleDummyClassifier(threshold=threshold)
            save_model(model, name, metadata)
        
        # 2. Lista todos os modelos
        all_models = list_models()
        assert len(all_models) == 3
        assert "random_forest_v1" in all_models
        assert "logistic_reg_v1" in all_models
        assert "svm_v1" in all_models
        
        # 3. Obtém resumo dos modelos
        summary = get_models_summary()
        assert len(summary) == 3
        
        # Verifica que o resumo contém as informações esperadas
        rf_summary = next(m for m in summary if m['name'] == 'random_forest_v1')
        assert rf_summary['accuracy'] == 0.92
        assert rf_summary['model_type'] == 'RandomForest'
        
        # 4. Carrega um modelo específico
        loaded_model = load_model("random_forest_v1")
        assert loaded_model is not None
        assert hasattr(loaded_model, 'predict')
        assert hasattr(loaded_model, 'predict_proba')
        
        # 5. Usa o modelo carregado para fazer previsões
        test_data = np.array([[10.0, 20.0, 5.0]])  # Lux, Temp, Vibração
        
        prediction = loaded_model.predict(test_data)
        assert prediction.shape == (1,)
        assert prediction[0] in [0, 1]
        
        # 6. Testa predict_proba
        probabilities = loaded_model.predict_proba(test_data)
        assert probabilities.shape == (1, 2)
        assert np.isclose(probabilities.sum(), 1.0)
        
    def test_model_selection_by_metric(self, temp_models_dir):
        """Testa seleção de modelos por métrica."""
        
        # Salva modelos com diferentes métricas
        models = [
            ("model_1", {"accuracy": 0.85, "f1": 0.82}),
            ("model_2", {"accuracy": 0.92, "f1": 0.90}),
            ("model_3", {"accuracy": 0.88, "f1": 0.85}),
            ("model_4", {"accuracy": 0.95, "f1": 0.93}),
            ("model_5", {"accuracy": 0.80, "f1": 0.78}),
        ]
        
        for name, metadata in models:
            model = SimpleDummyClassifier()
            save_model(model, name, metadata)
        
        # Obtém resumo e ordena por accuracy
        summary = get_models_summary()
        sorted_by_acc = sorted(summary, key=lambda x: x['accuracy'], reverse=True)
        
        # Verifica top 5
        assert len(sorted_by_acc) == 5
        assert sorted_by_acc[0]['name'] == 'model_4'  # accuracy 0.95
        assert sorted_by_acc[1]['name'] == 'model_2'  # accuracy 0.92
        assert sorted_by_acc[2]['name'] == 'model_3'  # accuracy 0.88
        
        # Carrega o melhor modelo
        best_model = load_model(sorted_by_acc[0]['name'])
        assert best_model is not None
        
    def test_sensor_data_prediction_simulation(self, temp_models_dir):
        """Simula previsão com dados de sensores reais."""
        
        # Salva um modelo
        model = SimpleDummyClassifier(threshold=15.0)
        save_model(
            model, 
            "sensor_classifier",
            {
                "accuracy": 0.91,
                "trained_on": "2024_sensor_data",
                "features": ["lux", "temperatura", "vibracao"]
            }
        )
        
        # Carrega o modelo
        loaded_model = load_model("sensor_classifier")
        
        # Simula leituras de sensores
        sensor_readings = [
            np.array([[15.0, 14.0, 0.0]]),  # Normal
            np.array([[50.0, 80.0, 100.0]]),  # Alta vibração - provável manutenção
            np.array([[10.0, 12.0, 1.0]]),  # Baixos valores
            np.array([[25.0, 30.0, 50.0]]),  # Valores médios-altos
        ]
        
        for reading in sensor_readings:
            prediction = loaded_model.predict(reading)
            probabilities = loaded_model.predict_proba(reading)
            
            # Validações básicas
            assert prediction[0] in [0, 1]
            assert probabilities.shape == (1, 2)
            assert 0 <= probabilities[0][0] <= 1
            assert 0 <= probabilities[0][1] <= 1
            assert np.isclose(probabilities[0].sum(), 1.0)
            
            # Probabilidade da classe predita deve ser a maior
            predicted_class = prediction[0]
            assert probabilities[0][predicted_class] >= probabilities[0][1 - predicted_class]
