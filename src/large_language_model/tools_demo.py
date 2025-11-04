"""
Example demonstrating how the new chatbot tools work together.

This script shows how tools are automatically discovered and can be invoked
by the LLM chatbot to perform various operations.
"""

from src.large_language_model.dynamic_tools import import_tools
from src.large_language_model.tipos_base.base_tools import BaseTool


def demonstrate_tool_discovery():
    """Demonstrate automatic tool discovery."""
    print("=" * 80)
    print("CHATBOT TOOLS - AUTOMATIC DISCOVERY DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Import all tools (automatic discovery)
    tools = import_tools(sort=True)
    
    print(f"📊 Total tools discovered: {len(tools)}\n")
    
    print("Available tools:")
    print("-" * 80)
    
    for i, (name, tool_class) in enumerate(tools.items(), 1):
        tool_instance = tool_class()
        func_name = tool_instance.function_name
        doc = tool_instance.function_declaration.__doc__
        
        # Extract first line of docstring
        first_line = doc.strip().split('\n')[0] if doc else "No description"
        
        print(f"{i}. {name}")
        print(f"   Function: {func_name}()")
        print(f"   Description: {first_line}")
        print()


def demonstrate_tool_structure():
    """Demonstrate tool structure and capabilities."""
    print("=" * 80)
    print("TOOL STRUCTURE DEMONSTRATION")
    print("=" * 80)
    print()
    
    tools = import_tools()
    
    # Pick one of the new tools to demonstrate
    tool_class = tools.get('ListarEquipamentosTool')
    
    if tool_class:
        tool = tool_class()
        
        print(f"Tool Class: {tool_class.__name__}")
        print(f"Function Name: {tool.function_name}")
        print(f"Chat Display: {tool.call_chat_display()}")
        print()
        
        print("Function Signature:")
        print(f"  {tool.function_declaration.__name__}{tool.function_declaration.__code__.co_varnames}")
        print()
        
        print("Full Docstring:")
        print("-" * 80)
        print(tool.function_declaration.__doc__)
        print("-" * 80)


def demonstrate_tool_capabilities():
    """Show what each new tool can do."""
    print("=" * 80)
    print("NEW TOOLS CAPABILITIES")
    print("=" * 80)
    print()
    
    capabilities = {
        "ListarEquipamentosTool": {
            "emoji": "📦",
            "purpose": "List all equipment",
            "when_to_use": [
                "User asks 'what equipment do we have?'",
                "User wants to see all registered equipment",
                "User needs equipment IDs for other operations"
            ]
        },
        "ListarSensoresTool": {
            "emoji": "📡",
            "purpose": "List sensors (all or by equipment)",
            "when_to_use": [
                "User asks 'what sensors are installed?'",
                "User wants sensors for specific equipment",
                "User needs sensor IDs for analysis"
            ]
        },
        "AgendarManutencaoTool": {
            "emoji": "📅",
            "purpose": "Schedule maintenance",
            "when_to_use": [
                "User wants to schedule maintenance",
                "ML prediction recommends maintenance",
                "User sets up preventive maintenance"
            ]
        },
        "EnviarNotificacaoTool": {
            "emoji": "📧",
            "purpose": "Send email notifications",
            "when_to_use": [
                "Alert about critical readings",
                "Notify about scheduled maintenance",
                "Send analysis reports"
            ]
        },
        "AnalisarDadosSensorTool": {
            "emoji": "📊",
            "purpose": "Statistical analysis of sensor data",
            "when_to_use": [
                "User asks 'how is sensor X behaving?'",
                "User wants statistical summary",
                "Before maintenance prediction"
            ]
        },
        "GerarGraficoLeiturasTool": {
            "emoji": "📈",
            "purpose": "Generate sensor reading graphs",
            "when_to_use": [
                "User asks for visual representation",
                "User wants to see trends over time",
                "Complement statistical analysis"
            ]
        },
        "PreverNecessidadeManutencaoTool": {
            "emoji": "🤖",
            "purpose": "ML-based maintenance prediction",
            "when_to_use": [
                "User asks 'does equipment need maintenance?'",
                "Proactive maintenance check",
                "After detecting anomalies"
            ]
        }
    }
    
    for tool_name, info in capabilities.items():
        print(f"{info['emoji']} {tool_name}")
        print(f"   Purpose: {info['purpose']}")
        print(f"   When to use:")
        for use_case in info['when_to_use']:
            print(f"     • {use_case}")
        print()


def demonstrate_conversation_flow():
    """Show example conversation flows using multiple tools."""
    print("=" * 80)
    print("EXAMPLE CONVERSATION FLOWS")
    print("=" * 80)
    print()
    
    scenarios = [
        {
            "title": "Scenario 1: Equipment Status Check",
            "user_query": "Tell me about equipment 1 and check if it needs maintenance",
            "tools_called": [
                ("ListarEquipamentosTool", "Get equipment details"),
                ("ListarSensoresTool", "List sensors for equipment 1"),
                ("PreverNecessidadeManutencaoTool", "Predict maintenance need"),
                ("AnalisarDadosSensorTool", "Analyze each sensor if prediction > 50%"),
            ],
            "expected_response": "Equipment details + sensor list + prediction + recommendation"
        },
        {
            "title": "Scenario 2: Sensor Analysis with Alert",
            "user_query": "Analyze sensor 1 from last week and alert if there's a problem",
            "tools_called": [
                ("AnalisarDadosSensorTool", "Analyze 7 days of data"),
                ("GerarGraficoLeiturasTool", "Generate visualization"),
                ("EnviarNotificacaoTool", "Send alert if anomalies detected"),
            ],
            "expected_response": "Statistical analysis + graph description + notification confirmation"
        },
        {
            "title": "Scenario 3: Proactive Maintenance Planning",
            "user_query": "Check all equipment and schedule maintenance for those that need it",
            "tools_called": [
                ("ListarEquipamentosTool", "Get all equipment"),
                ("PreverNecessidadeManutencaoTool", "Predict for each equipment"),
                ("AgendarManutencaoTool", "Schedule for high-probability equipment"),
                ("EnviarNotificacaoTool", "Notify maintenance team"),
            ],
            "expected_response": "Equipment list + predictions + scheduled maintenances + notifications"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['title']}")
        print("-" * 80)
        print(f"User Query: \"{scenario['user_query']}\"")
        print()
        print("LLM Process:")
        for j, (tool, reason) in enumerate(scenario['tools_called'], 1):
            print(f"  Step {j}: Call {tool}")
            print(f"          → {reason}")
        print()
        print(f"Expected Response: {scenario['expected_response']}")
        print()


def demonstrate_integration_with_llm():
    """Show how tools integrate with the LLM."""
    print("=" * 80)
    print("LLM INTEGRATION")
    print("=" * 80)
    print()
    
    print("How the LLM uses tools:")
    print()
    
    print("1. DISCOVERY PHASE")
    print("   • All tools are discovered at startup via dynamic_tools.py")
    print("   • Each tool is converted to a FunctionDeclaration")
    print("   • Declarations are registered with Google Gemini API")
    print()
    
    print("2. CONVERSATION PHASE")
    print("   • User sends a message")
    print("   • LLM analyzes: intent, entities, context")
    print("   • LLM matches to available tools based on docstrings")
    print()
    
    print("3. TOOL INVOCATION PHASE")
    print("   • LLM decides which tool(s) to call")
    print("   • LLM extracts parameters from user message")
    print("   • Tool is executed with extracted parameters")
    print()
    
    print("4. RESPONSE PHASE")
    print("   • Tool returns result (string)")
    print("   • LLM incorporates result into natural language response")
    print("   • User receives friendly, contextual answer")
    print()
    
    print("Example:")
    print("-" * 80)
    print("User: 'What sensors does equipment 2 have?'")
    print()
    print("LLM Analysis:")
    print("  • Intent: Query sensors")
    print("  • Entity: equipment_id = 2")
    print("  • Matching tool: listar_sensores(equipamento_id=2)")
    print()
    print("Tool Call:")
    print("  listar_sensores(equipamento_id=2)")
    print()
    print("Tool Result:")
    print("  'Total de 3 sensor(es) cadastrado(s) no equipamento ID 2:'")
    print("  '📡 ID: 5 - Sensor Temp 1...'")
    print()
    print("LLM Response:")
    print("  'O equipamento 2 possui 3 sensores instalados:")
    print("  1. Sensor de Temperatura (ID 5)")
    print("  2. Sensor de Vibração (ID 6)")
    print("  3. Sensor de Luminosidade (ID 7)'")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "CHATBOT TOOLS DEMONSTRATION" + " " * 31 + "║")
    print("║" + " " * 15 + "7 New Tools for Equipment Monitoring" + " " * 27 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    try:
        demonstrate_tool_discovery()
        print("\n")
        
        demonstrate_tool_structure()
        print("\n")
        
        demonstrate_tool_capabilities()
        print("\n")
        
        demonstrate_conversation_flow()
        print("\n")
        
        demonstrate_integration_with_llm()
        print("\n")
        
        print("=" * 80)
        print("✅ All demonstrations complete!")
        print("=" * 80)
        print()
        print("To use these tools:")
        print("  1. Start the dashboard: streamlit run main_dash.py")
        print("  2. Navigate to 🤖 Chat IA")
        print("  3. Ask natural language questions about equipment and sensors")
        print()
        print("Example questions:")
        print("  • 'Quais equipamentos temos?'")
        print("  • 'Analise o sensor 1 dos últimos 7 dias'")
        print("  • 'O equipamento 1 precisa de manutenção?'")
        print("  • 'Agende manutenção para o equipamento 2 no dia 31/12/2024'")
        print()
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
