"""
Testes para o módulo model_store.

Testa funcionalidades de:
- Salvar modelos
- Listar modelos
- Carregar modelos
- Gerenciar registro
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import joblib

from src.utils.model_store import (
    save_model,
    list_models,
    load_model,
    delete_model,
    get_model_metadata,
    get_models_summary,
    _load_registry,
    _save_registry,
    MODELS_DIR,
    REGISTRY_FILE
)


class DummyModel:
    """Modelo fictício para testes."""
    def __init__(self, name="DummyModel"):
        self.name = name
        self.param = 42
    
    def predict(self, X):
        return [1] * len(X)


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


class TestModelStore:
    """Testes para funcionalidades básicas do model_store."""
    
    def test_save_and_load_model(self, temp_models_dir):
        """Testa salvar e carregar um modelo."""
        model = DummyModel("TestModel")
        model_name = "test_model"
        metadata = {"accuracy": 0.95, "type": "dummy"}
        
        # Salva o modelo
        save_model(model, model_name, metadata)
        
        # Verifica se o arquivo foi criado
        expected_path = temp_models_dir / f"{model_name}.pkl"
        assert expected_path.exists()
        
        # Carrega o modelo
        loaded_model = load_model(model_name)
        
        # Verifica se o modelo carregado é equivalente
        assert loaded_model.name == model.name
        assert loaded_model.param == model.param
    
    def test_list_models(self, temp_models_dir):
        """Testa listagem de modelos."""
        # Salva alguns modelos
        for i in range(3):
            model = DummyModel(f"Model{i}")
            save_model(model, f"model_{i}", {"index": i})
        
        # Lista modelos
        models = list_models()
        
        assert len(models) == 3
        assert "model_0" in models
        assert "model_1" in models
        assert "model_2" in models
    
    def test_duplicate_model_name(self, temp_models_dir):
        """Testa que não permite salvar modelo com nome duplicado."""
        model = DummyModel()
        model_name = "duplicate_test"
        
        # Salva primeira vez
        save_model(model, model_name)
        
        # Tenta salvar novamente com mesmo nome
        with pytest.raises(ValueError, match="já existe"):
            save_model(model, model_name)
    
    def test_load_nonexistent_model(self, temp_models_dir):
        """Testa erro ao carregar modelo inexistente."""
        with pytest.raises(FileNotFoundError, match="não encontrado"):
            load_model("nonexistent_model")
    
    def test_get_model_metadata(self, temp_models_dir):
        """Testa obtenção de metadados de um modelo."""
        model = DummyModel()
        model_name = "metadata_test"
        metadata = {
            "accuracy": 0.92,
            "precision": 0.89,
            "model_type": "DummyClassifier"
        }
        
        save_model(model, model_name, metadata)
        
        # Obtém metadados
        info = get_model_metadata(model_name)
        
        assert "metadata" in info
        assert info["metadata"]["accuracy"] == 0.92
        assert "saved_at" in info
    
    def test_delete_model(self, temp_models_dir):
        """Testa exclusão de modelo."""
        model = DummyModel()
        model_name = "delete_test"
        
        save_model(model, model_name)
        
        # Verifica que foi criado
        assert model_name in list_models()
        
        # Deleta
        delete_model(model_name)
        
        # Verifica que foi removido
        assert model_name not in list_models()
        
        # Verifica que arquivo foi deletado
        expected_path = temp_models_dir / f"{model_name}.pkl"
        assert not expected_path.exists()
    
    def test_get_models_summary(self, temp_models_dir):
        """Testa obtenção de resumo de modelos."""
        # Salva modelos com diferentes metadados
        models_data = [
            ("model_a", {"accuracy": 0.91, "type": "rf"}),
            ("model_b", {"accuracy": 0.88, "type": "lr"}),
            ("model_c", {"accuracy": 0.95, "type": "svm"}),
        ]
        
        for name, metadata in models_data:
            model = DummyModel(name)
            save_model(model, name, metadata)
        
        # Obtém resumo
        summary = get_models_summary()
        
        assert len(summary) == 3
        
        # Verifica que todos têm os campos esperados
        for item in summary:
            assert "name" in item
            assert "saved_at" in item
            assert "accuracy" in item
            assert "type" in item
    
    def test_registry_persistence(self, temp_models_dir):
        """Testa que o registro persiste entre operações."""
        model = DummyModel()
        model_name = "persistence_test"
        metadata = {"test": "value"}
        
        save_model(model, model_name, metadata)
        
        # Lê diretamente o registry
        registry = _load_registry()
        
        assert model_name in registry
        assert registry[model_name]["metadata"]["test"] == "value"
    
    def test_empty_metadata(self, temp_models_dir):
        """Testa salvar modelo sem metadados."""
        model = DummyModel()
        model_name = "no_metadata"
        
        # Salva sem passar metadata
        save_model(model, model_name)
        
        # Verifica que foi salvo
        loaded = load_model(model_name)
        assert loaded.name == model.name
        
        # Verifica que metadados vazios foram criados
        info = get_model_metadata(model_name)
        assert "metadata" in info


class TestModelStoreEdgeCases:
    """Testes de casos extremos e edge cases."""
    
    def test_special_characters_in_name(self, temp_models_dir):
        """Testa nomes com caracteres especiais."""
        model = DummyModel()
        
        # Alguns caracteres devem funcionar
        valid_name = "model_2024-01-01_v1.0"
        save_model(model, valid_name)
        loaded = load_model(valid_name)
        assert loaded.name == model.name
    
    def test_concurrent_save_different_models(self, temp_models_dir):
        """Testa salvamento de modelos diferentes simultaneamente."""
        import threading
        import time
        
        results = []
        
        def save_model_thread(idx):
            try:
                time.sleep(0.01 * idx)  # Pequeno delay para evitar colisão exata
                model = DummyModel(f"Model{idx}")
                save_model(model, f"concurrent_{idx}_{time.time()}", {"index": idx})
                results.append(True)
            except Exception as e:
                results.append(False)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=save_model_thread, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verifica que todos foram salvos com sucesso
        assert len(results) == 5
        assert all(results)
        
        # Verifica que todos estão no registry
        models = list_models()
        assert len(models) == 5
    
    def test_load_corrupted_registry(self, temp_models_dir, monkeypatch):
        """Testa comportamento com registry corrompido."""
        # Cria registry inválido
        registry_path = temp_models_dir / "registry.json"
        registry_path.write_text("{ invalid json", encoding="utf-8")
        
        # Deve retornar dict vazio ao invés de crashar
        registry = _load_registry()
        assert registry == {}
    
    def test_model_file_deleted_but_in_registry(self, temp_models_dir):
        """Testa quando arquivo foi deletado mas está no registry."""
        model = DummyModel()
        model_name = "deleted_file"
        
        save_model(model, model_name)
        
        # Remove o arquivo mas não do registry
        model_path = temp_models_dir / f"{model_name}.pkl"
        model_path.unlink()
        
        # Deve dar erro ao tentar carregar
        with pytest.raises(FileNotFoundError):
            load_model(model_name)
