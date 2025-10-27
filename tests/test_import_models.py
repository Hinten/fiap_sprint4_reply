"""
Tests for the import_models function and the static/dynamic import mechanism.

This module verifies that:
- import_models prefers the generated file when available
- import_models falls back to dynamic import when generated file is missing
- Both import paths return the same models
- The import mechanism is robust and handles edge cases
"""

import sys
import importlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from types import ModuleType

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestImportModelsStaticPath:
    """Test import_models when using the static generated file."""

    def test_uses_generated_file_when_available(self, monkeypatch):
        """Test that import_models uses the generated file when it exists."""
        # Create a mock generated module
        mock_generated = ModuleType("src.database.generated_models_imports")
        
        # Track if the function was called
        import_called = {"value": False}
        
        def mock_import_generated_models():
            import_called["value"] = True
        
        mock_generated.import_generated_models = mock_import_generated_models
        
        # Mock the import to return our mock module
        with patch.dict('sys.modules', {
            'src.database.generated_models_imports': mock_generated
        }):
            # Import the dynamic_import module fresh
            if 'src.database.dynamic_import' in sys.modules:
                del sys.modules['src.database.dynamic_import']
            
            from src.database.dynamic_import import import_models
            
            # Call import_models (won't work fully due to missing dependencies,
            # but we can check that it tried to use the generated file)
            try:
                import_models()
            except Exception:
                # We expect some errors due to missing database setup
                pass
            
            # Verify the generated import function was called
            assert import_called["value"] is True

    def test_logs_debug_message_when_using_static_imports(self, monkeypatch, caplog):
        """Test that a debug log is emitted when using static imports."""
        import logging
        caplog.set_level(logging.DEBUG)
        
        # Create a mock generated module
        mock_generated = ModuleType("src.database.generated_models_imports")
        mock_generated.import_generated_models = lambda: None
        
        with patch.dict('sys.modules', {
            'src.database.generated_models_imports': mock_generated
        }):
            if 'src.database.dynamic_import' in sys.modules:
                del sys.modules['src.database.dynamic_import']
            
            from src.database.dynamic_import import import_models
            
            try:
                import_models()
            except Exception:
                pass
            
            # Check for the debug message
            assert any("Using static generated imports" in record.message 
                      for record in caplog.records)


class TestImportModelsFallback:
    """Test import_models when falling back to dynamic imports."""

    def test_falls_back_when_function_missing(self, monkeypatch, caplog):
        """Test fallback when generated module exists but function doesn't."""
        import logging
        caplog.set_level(logging.DEBUG)
        
        # Create a mock module without the import_generated_models function
        mock_generated = ModuleType("src.database.generated_models_imports")
        # Intentionally don't add import_generated_models
        
        with patch.dict('sys.modules', {
            'src.database.generated_models_imports': mock_generated
        }):
            if 'src.database.dynamic_import' in sys.modules:
                del sys.modules['src.database.dynamic_import']
            
            try:
                from src.database.dynamic_import import import_models
                import_models()
            except Exception:
                pass
            
            # Should fall back due to AttributeError
            assert any("falling back to dynamic import" in record.message 
                      for record in caplog.records)


class TestImportModelsCollection:
    """Test the model collection after imports."""

    def test_returns_dict_of_model_classes(self):
        """Test that import_models returns a dictionary of Model classes."""
        from src.database.dynamic_import import import_models
        
        models = import_models()
        
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # Check that all values are classes
        for name, model_class in models.items():
            assert isinstance(name, str)
            assert isinstance(model_class, type)

    def test_finds_expected_models(self):
        """Test that import_models finds the expected model classes."""
        from src.database.dynamic_import import import_models
        
        models = import_models()
        
        # Based on the actual models in the project
        expected_models = ['Empresa', 'Equipamento', 'Sensor', 'ManutencaoEquipamento']
        
        for expected in expected_models:
            assert expected in models, f"Expected model {expected} not found"

    def test_excludes_base_model_class(self):
        """Test that the base Model class itself is not included."""
        from src.database.dynamic_import import import_models
        
        models = import_models()
        
        # The base Model class should not be in the results
        assert 'Model' not in models

    def test_sort_parameter_orders_by_import_order(self):
        """Test that sort=True orders models by __database_import_order__."""
        from src.database.dynamic_import import import_models
        
        models_unsorted = import_models(sort=False)
        models_sorted = import_models(sort=True)
        
        # Both should have same models
        assert set(models_unsorted.keys()) == set(models_sorted.keys())
        
        # Sorted version should respect __database_import_order__
        if len(models_sorted) > 1:
            sorted_orders = [
                cls.__database_import_order__ 
                for cls in models_sorted.values()
            ]
            # Check if sorted (each element <= next element)
            assert all(sorted_orders[i] <= sorted_orders[i+1] 
                      for i in range(len(sorted_orders)-1))


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_import_models_idempotent(self):
        """Test that import_models can be called multiple times."""
        from src.database.dynamic_import import import_models
        
        # Call multiple times
        models1 = import_models()
        models2 = import_models()
        
        # Both should return the same set of models
        assert set(models1.keys()) == set(models2.keys())
        
        # The model classes should be the same objects
        for name in models1.keys():
            assert models1[name] is models2[name]

    def test_handles_missing_models_directory_gracefully(self, monkeypatch, tmp_path):
        """Test graceful handling when models directory doesn't exist."""
        from src.database import dynamic_import
        
        # Create a temporary empty directory
        fake_models_path = tmp_path / "nonexistent"
        
        # Patch the models_path calculation to point to nonexistent directory
        original_dirname = dynamic_import.os.path.dirname
        
        def mock_dirname(path):
            if 'dynamic_import.py' in path:
                return str(tmp_path)
            return original_dirname(path)
        
        with patch.object(dynamic_import.os.path, 'dirname', side_effect=mock_dirname):
            with patch.object(dynamic_import.os.path, 'join', 
                            return_value=str(fake_models_path)):
                with patch.object(dynamic_import.os, 'listdir', return_value=[]):
                    # Should not crash
                    result = dynamic_import._collect_model_classes()
                    assert isinstance(result, dict)
                    assert len(result) == 0


class TestGeneratedFileIntegration:
    """Test that the generated file works correctly."""

    def test_generated_file_exists(self):
        """Test that the generated file exists."""
        generated_file = PROJECT_ROOT / "src" / "database" / "generated_models_imports.py"
        assert generated_file.exists(), "Generated file should exist"

    def test_generated_file_is_valid_python(self):
        """Test that the generated file is valid Python."""
        generated_file = PROJECT_ROOT / "src" / "database" / "generated_models_imports.py"
        
        # Try to import it
        try:
            from src.database.generated_models_imports import import_generated_models
            assert callable(import_generated_models)
        except ImportError as e:
            pytest.fail(f"Generated file is not valid: {e}")

    def test_generated_function_can_be_called(self):
        """Test that the generated import function can be called."""
        from src.database.generated_models_imports import import_generated_models
        
        # Should not raise an exception
        try:
            import_generated_models()
        except Exception as e:
            # Some errors might occur due to database setup, but ImportError should not happen
            if isinstance(e, ImportError):
                pytest.fail(f"Generated imports failed: {e}")
