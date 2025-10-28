"""
Tests for the generative AI chat functionality.
"""
import pytest
from src.large_language_model.dynamic_tools import import_tools, get_tool_by_name
from src.large_language_model.tools.datetime_tool import DateTimeTool
from src.large_language_model.client import AvailableGenerativeModels
from datetime import datetime


class TestToolDiscovery:
    """Test the dynamic tool discovery system."""
    
    def test_import_tools_finds_datetime_tool(self):
        """Test that the datetime tool is discovered."""
        tools = import_tools()
        assert "DateTimeTool" in tools
        assert tools["DateTimeTool"] == DateTimeTool
    
    def test_import_tools_sorted(self):
        """Test that tools can be sorted."""
        tools = import_tools(sort=True)
        assert isinstance(tools, dict)
        assert len(tools) > 0
    
    def test_get_tool_by_name(self):
        """Test retrieving a tool by name."""
        tool_class = get_tool_by_name("DateTimeTool")
        assert tool_class == DateTimeTool
    
    def test_get_tool_by_name_not_found(self):
        """Test that getting a non-existent tool raises error."""
        with pytest.raises(ValueError, match="não encontrada"):
            get_tool_by_name("NonExistentTool")


class TestDateTimeTool:
    """Test the DateTimeTool functionality."""
    
    def test_datetime_tool_instantiation(self):
        """Test that DateTimeTool can be instantiated."""
        tool = DateTimeTool()
        assert tool is not None
    
    def test_datetime_tool_execute(self):
        """Test that DateTimeTool returns a valid ISO format datetime."""
        tool = DateTimeTool()
        result = tool.execute()
        
        # Should be a string
        assert isinstance(result, str)
        
        # Should be parseable as ISO datetime
        parsed = datetime.fromisoformat(result)
        assert parsed is not None
    
    def test_datetime_tool_call_chat_display(self):
        """Test chat display message."""
        tool = DateTimeTool()
        display = tool.call_chat_display()
        assert isinstance(display, str)
        assert len(display) > 0
    
    def test_datetime_tool_call_result_display(self):
        """Test result display message."""
        tool = DateTimeTool()
        result = "2025-10-28T12:00:00"
        display = tool.call_result_display(result)
        assert isinstance(display, str)
        assert result in display


class TestGenerativeModels:
    """Test the generative model enums."""
    
    def test_available_models_enum(self):
        """Test that available models enum is defined."""
        assert AvailableGenerativeModels.GEMINI_2_0_FLASH
        assert AvailableGenerativeModels.GEMINI_2_0_FLASH_LITE
    
    def test_model_enum_values(self):
        """Test model enum values."""
        assert AvailableGenerativeModels.GEMINI_2_0_FLASH.value == 'gemini-2.0-flash'
        assert AvailableGenerativeModels.GEMINI_2_0_FLASH_LITE.value == 'gemini-2.0-flash-lite'
    
    def test_model_enum_str_representation(self):
        """Test string representation of models."""
        assert str(AvailableGenerativeModels.GEMINI_2_0_FLASH) == "Gemini 2.0 Flash"
        assert str(AvailableGenerativeModels.GEMINI_2_0_FLASH_LITE) == "Gemini 2.0 Flash Lite"


class TestToolBase:
    """Test the BaseTool abstract class implementation."""
    
    def test_tool_has_function_declaration(self):
        """Test that tool has function declaration."""
        tool = DateTimeTool()
        assert hasattr(tool, 'function_declaration')
        assert callable(tool.function_declaration)
    
    def test_tool_function_has_docstring(self):
        """Test that function declaration has a docstring."""
        tool = DateTimeTool()
        assert tool.function_declaration.__doc__ is not None
        assert len(tool.function_declaration.__doc__.strip()) > 0
    
    def test_tool_function_name(self):
        """Test that tool has correct function name."""
        tool = DateTimeTool()
        assert tool.function_name == "get_current_time"
