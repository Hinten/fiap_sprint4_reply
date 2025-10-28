"""
Tests for the static code generator (generate_model_imports.py).

This module verifies that the generator correctly:
- Detects Python files containing Model subclasses
- Generates the expected output file with correct imports
- Handles edge cases (no models, syntax errors, etc.)
"""

import ast
import sys
from pathlib import Path
from textwrap import dedent

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from generators.generate_model_imports import (
    file_contains_model_subclass,
    find_modules_with_models,
    generate_imports_file,
)


class TestFileContainsModelSubclass:
    """Test the AST-based Model subclass detection."""

    def test_detects_simple_model_subclass(self, tmp_path):
        """Test detection of class Foo(Model)."""
        test_file = tmp_path / "test_model.py"
        test_file.write_text(dedent("""
            from src.database.tipos_base.model import Model
            
            class TestModel(Model):
                pass
        """))
        
        assert file_contains_model_subclass(test_file) is True

    def test_detects_model_with_attribute_base(self, tmp_path):
        """Test detection of class Foo(module.Model)."""
        test_file = tmp_path / "test_model.py"
        test_file.write_text(dedent("""
            import src.database.tipos_base.model as m
            
            class TestModel(m.Model):
                pass
        """))
        
        assert file_contains_model_subclass(test_file) is True

    def test_ignores_file_without_model(self, tmp_path):
        """Test that files without Model subclasses are not detected."""
        test_file = tmp_path / "not_a_model.py"
        test_file.write_text(dedent("""
            class RegularClass:
                pass
            
            class AnotherClass(object):
                pass
        """))
        
        assert file_contains_model_subclass(test_file) is False

    def test_handles_syntax_error_gracefully(self, tmp_path):
        """Test that syntax errors are handled without crashing."""
        test_file = tmp_path / "syntax_error.py"
        test_file.write_text("def broken(:\n    pass")
        
        # Should return False and not raise an exception
        assert file_contains_model_subclass(test_file) is False

    def test_ignores_model_as_string(self, tmp_path):
        """Test that 'Model' as a string doesn't trigger detection."""
        test_file = tmp_path / "model_string.py"
        test_file.write_text(dedent("""
            class SomeClass:
                name = "Model"
        """))
        
        assert file_contains_model_subclass(test_file) is False


class TestFindModulesWithModels:
    """Test the directory scanning functionality."""

    def test_finds_models_in_flat_directory(self, tmp_path):
        """Test finding models in a single directory."""
        # Create a temporary models directory structure
        project_root = tmp_path
        models_dir = tmp_path / "src" / "database" / "models"
        models_dir.mkdir(parents=True)
        
        # Create model files
        (models_dir / "empresa.py").write_text(dedent("""
            from src.database.tipos_base.model import Model
            class Empresa(Model):
                pass
        """))
        
        (models_dir / "sensor.py").write_text(dedent("""
            from src.database.tipos_base.model import Model
            class Sensor(Model):
                pass
        """))
        
        # Create non-model file
        (models_dir / "utils.py").write_text("def helper(): pass")
        
        # Create __init__.py (should be ignored)
        (models_dir / "__init__.py").write_text("")
        
        # Test the function with explicit project_root
        modules = find_modules_with_models(models_dir, project_root)
        
        assert len(modules) == 2
        assert "src.database.models.empresa" in modules
        assert "src.database.models.sensor" in modules
        assert "src.database.models.utils" not in modules

    def test_finds_models_recursively(self, tmp_path):
        """Test finding models in nested directories."""
        project_root = tmp_path
        models_dir = tmp_path / "src" / "database" / "models"
        models_dir.mkdir(parents=True)
        subdir = models_dir / "subdirectory"
        subdir.mkdir()
        
        (models_dir / "model1.py").write_text(dedent("""
            from src.database.tipos_base.model import Model
            class Model1(Model):
                pass
        """))
        
        (subdir / "model2.py").write_text(dedent("""
            from src.database.tipos_base.model import Model
            class Model2(Model):
                pass
        """))
        
        modules = find_modules_with_models(models_dir, project_root)
        
        assert len(modules) == 2
        assert "src.database.models.model1" in modules
        assert "src.database.models.subdirectory.model2" in modules

    def test_handles_empty_directory(self, tmp_path):
        """Test behavior with an empty directory."""
        models_dir = tmp_path / "empty"
        models_dir.mkdir()
        
        modules = find_modules_with_models(models_dir)
        
        assert modules == []

    def test_handles_nonexistent_directory(self, tmp_path):
        """Test behavior with a directory that doesn't exist."""
        nonexistent = tmp_path / "does_not_exist"
        
        modules = find_modules_with_models(nonexistent)
        
        assert modules == []


class TestGenerateImportsFile:
    """Test the code generation functionality."""

    def test_generates_file_with_multiple_modules(self, tmp_path):
        """Test generating imports file with multiple modules."""
        output_file = tmp_path / "generated_imports.py"
        modules = [
            "src.database.models.empresa",
            "src.database.models.sensor",
            "src.database.models.equipamento",
        ]
        
        generate_imports_file(modules, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        
        # Check file contains expected elements
        assert "AUTOGENERATED FILE" in content
        assert "import importlib" in content
        assert "def import_generated_models()" in content  # Allow for type hints
        assert 'importlib.import_module("src.database.models.empresa")' in content
        assert 'importlib.import_module("src.database.models.sensor")' in content
        assert 'importlib.import_module("src.database.models.equipamento")' in content
        assert "logger.error" in content  # Error handling

    def test_generates_file_with_no_modules(self, tmp_path):
        """Test generating imports file when no modules are found."""
        output_file = tmp_path / "generated_imports_empty.py"
        modules = []
        
        generate_imports_file(modules, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        
        assert "No model modules found" in content
        assert "pass" in content

    def test_generated_file_is_valid_python(self, tmp_path):
        """Test that the generated file is syntactically valid Python."""
        output_file = tmp_path / "generated_valid.py"
        modules = ["src.database.models.test"]
        
        generate_imports_file(modules, output_file)
        
        # Try to parse the generated file
        content = output_file.read_text()
        tree = ast.parse(content)
        
        # Verify it's valid Python with expected structure
        assert tree is not None
        assert any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))

    def test_generated_file_has_correct_function_name(self, tmp_path):
        """Test that the generated function has the expected name."""
        output_file = tmp_path / "generated_func.py"
        modules = ["src.database.models.test"]
        
        generate_imports_file(modules, output_file)
        
        content = output_file.read_text()
        tree = ast.parse(content)
        
        func_names = [
            node.name for node in ast.walk(tree) 
            if isinstance(node, ast.FunctionDef)
        ]
        
        assert "import_generated_models" in func_names


class TestIntegration:
    """Integration tests that verify the full workflow."""

    def test_full_workflow(self, tmp_path, monkeypatch):
        """Test the complete workflow from scanning to generation."""
        # Setup: Create a fake project structure
        project_root = tmp_path / "project"
        models_dir = project_root / "src" / "database" / "models"
        models_dir.mkdir(parents=True)
        
        (models_dir / "empresa.py").write_text(dedent("""
            from src.database.tipos_base.model import Model
            class Empresa(Model):
                __tablename__ = "empresa"
        """))
        
        (models_dir / "sensor.py").write_text(dedent("""
            from src.database.tipos_base.model import Model
            class Sensor(Model):
                __tablename__ = "sensor"
        """))
        
        # Generate output
        output_file = project_root / "src" / "database" / "generated_models_imports.py"
        
        # Patch PROJECT_ROOT in the module
        import generators.generate_model_imports as gen_module
        original_root = gen_module.PROJECT_ROOT
        original_models_dir = gen_module.MODELS_DIR
        original_output = gen_module.OUTPUT_FILE
        
        try:
            monkeypatch.setattr(gen_module, "PROJECT_ROOT", project_root)
            monkeypatch.setattr(gen_module, "MODELS_DIR", models_dir)
            monkeypatch.setattr(gen_module, "OUTPUT_FILE", output_file)
            
            # Run the workflow
            modules = find_modules_with_models(models_dir, project_root)
            generate_imports_file(modules, output_file)
            
            # Verify
            assert output_file.exists()
            content = output_file.read_text()
            assert "src.database.models.empresa" in content
            assert "src.database.models.sensor" in content
            
        finally:
            # Restore original values
            monkeypatch.setattr(gen_module, "PROJECT_ROOT", original_root)
            monkeypatch.setattr(gen_module, "MODELS_DIR", original_models_dir)
            monkeypatch.setattr(gen_module, "OUTPUT_FILE", original_output)
