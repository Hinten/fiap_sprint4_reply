"""
Unit tests for new chatbot tools.
Tests all 7 new tools: equipment listing, sensor listing, maintenance scheduling,
notifications, data analysis, graph generation, and maintenance prediction.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, date

# Import all new tools
from src.large_language_model.tools.listar_equipamentos_tool import (
    ListarEquipamentosTool, listar_equipamentos
)
from src.large_language_model.tools.listar_sensores_tool import (
    ListarSensoresTool, listar_sensores
)
from src.large_language_model.tools.agendar_manutencao_tool import (
    AgendarManutencaoTool, agendar_manutencao
)
from src.large_language_model.tools.enviar_notificacao_tool import (
    EnviarNotificacaoTool, enviar_notificacao
)
from src.large_language_model.tools.analisar_dados_sensor_tool import (
    AnalisarDadosSensorTool, analisar_dados_sensor
)
from src.large_language_model.tools.gerar_grafico_leituras_tool import (
    GerarGraficoLeiturasTool, gerar_grafico_leituras
)
from src.large_language_model.tools.prever_necessidade_manutencao_tool import (
    PreverNecessidadeManutencaoTool, prever_necessidade_manutencao
)
from src.large_language_model.tools.prever_por_valores_tool import (
    PreverManutencaoPorValoresTool, prever_manutencao_por_valores
)
from src.large_language_model.tools.obter_leitura_mais_recente_sensor_tool import (
    ObterLeituraMaisRecenteSensorTool, obter_leitura_mais_recente_sensor
)


class TestListarEquipamentosTool:
    """Tests for equipment listing tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = ListarEquipamentosTool()
        assert tool is not None
        assert tool.function_name == "listar_equipamentos"
    
    def test_tool_has_docstring(self):
        """Test that the function has a docstring."""
        tool = ListarEquipamentosTool()
        assert tool.function_declaration.__doc__ is not None
        assert len(tool.function_declaration.__doc__.strip()) > 0
    
    @patch('src.large_language_model.tools.listar_equipamentos_tool.Equipamento')
    def test_listar_equipamentos_empty(self, mock_equipamento):
        """Test listing when no equipment exists."""
        mock_equipamento.all.return_value = []
        result = listar_equipamentos()
        assert "Nenhum equipamento cadastrado" in result
    
    @patch('src.large_language_model.tools.listar_equipamentos_tool.Equipamento')
    def test_listar_equipamentos_with_data(self, mock_equipamento):
        """Test listing with equipment data."""
        mock_equip = Mock()
        mock_equip.id = 1
        mock_equip.nome = "Bomba Hidráulica"
        mock_equip.modelo = "BH-2000"
        mock_equip.localizacao = "Setor A"
        mock_equip.data_instalacao = datetime(2023, 1, 15)
        mock_equip.sensores = [Mock(), Mock()]
        mock_equip.descricao = "Bomba principal"
        
        mock_equipamento.all.return_value = [mock_equip]
        result = listar_equipamentos()
        
        assert "1 equipamento(s)" in result
        assert "Bomba Hidráulica" in result
        assert "BH-2000" in result
        assert "Setor A" in result
        assert "Sensores: 2" in result
    
    def test_call_chat_display(self):
        """Test chat display message."""
        tool = ListarEquipamentosTool()
        message = tool.call_chat_display()
        assert "📦" in message or "Listando" in message
    
    def test_call_result_display(self):
        """Test result display message."""
        tool = ListarEquipamentosTool()
        result = "Test result"
        display = tool.call_result_display(result)
        assert result in display


class TestListarSensoresTool:
    """Tests for sensor listing tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = ListarSensoresTool()
        assert tool is not None
        assert tool.function_name == "listar_sensores"
    
    @patch('src.large_language_model.tools.listar_sensores_tool.Sensor')
    def test_listar_sensores_empty(self, mock_sensor):
        """Test listing when no sensors exist."""
        mock_sensor.all.return_value = []
        result = listar_sensores()
        assert "Nenhum sensor cadastrado" in result
    
    @patch('src.large_language_model.tools.listar_sensores_tool.Sensor')
    def test_listar_sensores_with_data(self, mock_sensor):
        """Test listing with sensor data."""
        mock_tipo = Mock()
        mock_tipo.nome = "Temperatura"
        mock_tipo.tipo = "T"
        
        mock_equip = Mock()
        mock_equip.nome = "Equipamento 1"
        mock_equip.id = 1
        
        mock_sens = Mock()
        mock_sens.id = 1
        mock_sens.nome = "Sensor Temp 1"
        mock_sens.tipo_sensor = mock_tipo
        mock_sens.equipamento = mock_equip
        mock_sens.equipamento_id = 1
        mock_sens.cod_serial = "SN001"
        mock_sens.limiar_manutencao_maior = 80.0
        mock_sens.limiar_manutencao_menor = 10.0
        mock_sens.data_instalacao = datetime(2023, 1, 15)
        mock_sens.descricao = "Sensor principal"
        
        mock_sensor.all.return_value = [mock_sens]
        result = listar_sensores()
        
        assert "1 sensor(es)" in result
        assert "Sensor Temp 1" in result
        assert "Temperatura" in result
    
    @patch('src.large_language_model.tools.listar_sensores_tool.Sensor')
    def test_listar_sensores_by_equipamento(self, mock_sensor):
        """Test filtering sensors by equipment."""
        mock_sens1 = Mock()
        mock_sens1.equipamento_id = 1
        mock_sens1.id = 1
        mock_sens1.nome = "Sensor 1"
        mock_sens1.tipo_sensor = None
        mock_sens1.equipamento = None
        mock_sens1.cod_serial = None
        mock_sens1.limiar_manutencao_maior = None
        mock_sens1.limiar_manutencao_menor = None
        mock_sens1.data_instalacao = None
        mock_sens1.descricao = None
        
        mock_sens2 = Mock()
        mock_sens2.equipamento_id = 2
        
        mock_sensor.all.return_value = [mock_sens1, mock_sens2]
        result = listar_sensores(equipamento_id=1)
        
        assert "equipamento ID 1" in result
        assert "Sensor 1" in result


class TestAgendarManutencaoTool:
    """Tests for maintenance scheduling tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = AgendarManutencaoTool()
        assert tool is not None
        assert tool.function_name == "agendar_manutencao"
    
    @patch('src.large_language_model.tools.agendar_manutencao_tool.Equipamento')
    def test_agendar_manutencao_equipamento_not_found(self, mock_equipamento):
        """Test scheduling when equipment doesn't exist."""
        mock_equipamento.get_from_id.return_value = None
        result = agendar_manutencao(
            equipamento_id=999,
            data_previsao="2024-12-31",
            motivo="Teste"
        )
        assert "não encontrado" in result
    
    @patch('src.large_language_model.tools.agendar_manutencao_tool.ManutencaoEquipamento')
    @patch('src.large_language_model.tools.agendar_manutencao_tool.Equipamento')
    def test_agendar_manutencao_success(self, mock_equipamento, mock_manutencao):
        """Test successful maintenance scheduling."""
        mock_equip = Mock()
        mock_equip.id = 1
        mock_equip.nome = "Equipamento Teste"
        mock_equipamento.get_from_id.return_value = mock_equip
        
        mock_man = Mock()
        mock_man.id = 1
        mock_man.save = Mock()
        mock_manutencao.return_value = mock_man
        
        result = agendar_manutencao(
            equipamento_id=1,
            data_previsao="2025-12-31",
            motivo="Manutenção preventiva"
        )
        
        assert "agendada com sucesso" in result
        assert "Equipamento Teste" in result
    
    @patch('src.large_language_model.tools.agendar_manutencao_tool.Equipamento')
    def test_agendar_manutencao_invalid_date(self, mock_equipamento):
        """Test with invalid date format."""
        mock_equip = Mock()
        mock_equip.id = 1
        mock_equipamento.get_from_id.return_value = mock_equip
        
        result = agendar_manutencao(
            equipamento_id=1,
            data_previsao="invalid-date",
            motivo="Teste"
        )
        assert "Erro" in result or "inválido" in result


class TestEnviarNotificacaoTool:
    """Tests for notification sending tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = EnviarNotificacaoTool()
        assert tool is not None
        assert tool.function_name == "enviar_notificacao"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_enviar_notificacao_no_config(self):
        """Test sending notification without configuration."""
        result = enviar_notificacao("Test", "Test message")
        assert "não estão configuradas" in result
    
    @patch('src.large_language_model.tools.enviar_notificacao_tool.enviar_email')
    @patch.dict('os.environ', {'SNS_TOPIC_ARN': 'arn:test', 'SNS_REGION': 'us-east-1'})
    def test_enviar_notificacao_success(self, mock_enviar):
        """Test successful notification sending."""
        mock_enviar.return_value = {'MessageId': '123456'}
        
        result = enviar_notificacao("Alerta", "Temperatura alta detectada")
        
        assert "sucesso" in result
        assert "MessageId" in result or "123456" in result
    
    @patch('src.large_language_model.tools.enviar_notificacao_tool.enviar_email')
    @patch.dict('os.environ', {'SNS_TOPIC_ARN': 'arn:test', 'SNS_REGION': 'us-east-1'})
    def test_enviar_notificacao_long_subject(self, mock_enviar):
        """Test with long subject that needs truncation."""
        mock_enviar.return_value = {'MessageId': '123456'}
        
        long_subject = "A" * 150  # 150 characters
        result = enviar_notificacao(long_subject, "Message")
        
        # Should truncate and still succeed
        mock_enviar.assert_called_once()
        call_args = mock_enviar.call_args
        assert len(call_args[1]['assunto']) <= 100


class TestAnalisarDadosSensorTool:
    """Tests for sensor data analysis tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = AnalisarDadosSensorTool()
        assert tool is not None
        assert tool.function_name == "analisar_dados_sensor"
    
    @patch('src.large_language_model.tools.analisar_dados_sensor_tool.Sensor')
    def test_analisar_dados_sensor_not_found(self, mock_sensor):
        """Test analysis when sensor doesn't exist."""
        mock_sensor.get_from_id.return_value = None
        result = analisar_dados_sensor(sensor_id=999)
        assert "não encontrado" in result
    
    @patch('src.large_language_model.tools.analisar_dados_sensor_tool.LeituraSensor')
    @patch('src.large_language_model.tools.analisar_dados_sensor_tool.Sensor')
    def test_analisar_dados_no_readings(self, mock_sensor, mock_leitura):
        """Test analysis when no readings exist."""
        mock_sens = Mock()
        mock_sens.id = 1
        mock_sens.nome = "Sensor Teste"
        mock_sensor.get_from_id.return_value = mock_sens
        
        mock_leitura.get_leituras_for_sensor.return_value = []
        
        result = analisar_dados_sensor(sensor_id=1)
        assert "Nenhuma leitura encontrada" in result
    
    @patch('src.large_language_model.tools.analisar_dados_sensor_tool.LeituraSensor')
    @patch('src.large_language_model.tools.analisar_dados_sensor_tool.Sensor')
    def test_analisar_dados_with_readings(self, mock_sensor, mock_leitura):
        """Test analysis with sensor readings."""
        mock_tipo = Mock()
        mock_tipo.nome = "Temperatura"
        mock_tipo.tipo = "T"
        
        mock_sens = Mock()
        mock_sens.id = 1
        mock_sens.nome = "Sensor Temp"
        mock_sens.tipo_sensor = mock_tipo
        mock_sens.equipamento = None
        mock_sens.limiar_manutencao_maior = 80.0
        mock_sens.limiar_manutencao_menor = 10.0
        mock_sensor.get_from_id.return_value = mock_sens
        
        # Create mock readings
        mock_readings = []
        for i in range(10):
            mock_reading = Mock()
            mock_reading.valor = 25.0 + i  # Values from 25 to 34
            mock_readings.append(mock_reading)
        
        mock_leitura.get_leituras_for_sensor.return_value = mock_readings
        
        result = analisar_dados_sensor(sensor_id=1, dias=7)
        
        assert "Análise de Dados" in result
        assert "ESTATÍSTICAS" in result
        assert "Média" in result
        assert "TENDÊNCIA" in result


class TestGerarGraficoLeiturasTool:
    """Tests for graph generation tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = GerarGraficoLeiturasTool()
        assert tool is not None
        assert tool.function_name == "gerar_grafico_leituras"
    
    @patch('src.large_language_model.tools.gerar_grafico_leituras_tool.Database')
    def test_gerar_grafico_sensor_not_found(self, mock_database):
        """Test graph generation when sensor doesn't exist."""
        # Mock the session context manager
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.query.return_value.options.return_value.filter.return_value.one_or_none.return_value = None
        mock_database.get_session.return_value = mock_session
        
        result = gerar_grafico_leituras(sensor_id=999)
        assert isinstance(result, dict)
        assert "erro" in result
        assert "não encontrado" in result["erro"]
    
    @patch('src.large_language_model.tools.gerar_grafico_leituras_tool.LeituraSensor')
    @patch('src.large_language_model.tools.gerar_grafico_leituras_tool.Database')
    def test_gerar_grafico_no_readings(self, mock_database, mock_leitura):
        """Test graph generation when no readings exist."""
        mock_sens = Mock()
        mock_sens.id = 1
        mock_sens.nome = "Sensor Teste"
        
        # Mock the session context manager
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.query.return_value.options.return_value.filter.return_value.one_or_none.return_value = mock_sens
        mock_database.get_session.return_value = mock_session
        
        mock_leitura.get_leituras_for_sensor.return_value = []
        
        result = gerar_grafico_leituras(sensor_id=1)
        assert isinstance(result, dict)
        assert "erro" in result
        assert "Nenhuma leitura encontrada" in result["erro"]
    
    @patch('src.large_language_model.tools.gerar_grafico_leituras_tool.tempfile.NamedTemporaryFile')
    @patch('src.large_language_model.tools.gerar_grafico_leituras_tool.plt')
    @patch('src.large_language_model.tools.gerar_grafico_leituras_tool.LeituraSensor')
    @patch('src.large_language_model.tools.gerar_grafico_leituras_tool.Database')
    def test_gerar_grafico_with_readings(self, mock_database, mock_leitura, mock_plt, mock_tempfile):
        """Test graph generation with readings."""
        mock_tipo = Mock()
        mock_tipo.nome = "Temperatura"
        mock_tipo.tipo = "T"
        
        mock_sens = Mock()
        mock_sens.id = 1
        mock_sens.nome = "Sensor Temp"
        mock_sens.tipo_sensor = mock_tipo
        mock_sens.equipamento = None
        mock_sens.limiar_manutencao_maior = None
        mock_sens.limiar_manutencao_menor = None
        
        # Mock the session context manager
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session.query.return_value.options.return_value.filter.return_value.one_or_none.return_value = mock_sens
        mock_database.get_session.return_value = mock_session
        
        # Create mock readings
        mock_readings = []
        base_time = datetime.now()
        for i in range(10):
            mock_reading = Mock()
            mock_reading.valor = 25.0 + i
            mock_reading.data_leitura = base_time + timedelta(hours=i)
            mock_readings.append(mock_reading)
        
        mock_leitura.get_leituras_for_sensor.return_value = mock_readings
        
        # Mock matplotlib
        mock_plt.figure.return_value = Mock()
        
        # Mock tempfile
        mock_temp = Mock()
        mock_temp.name = '/tmp/test_graph.png'
        mock_temp.write = Mock()
        mock_temp.close = Mock()
        mock_tempfile.return_value = mock_temp
        
        result = gerar_grafico_leituras(sensor_id=1, dias=7)
        
        assert isinstance(result, dict)
        assert "sensor_id" in result
        assert result["sensor_id"] == 1
        assert "estatisticas" in result
        assert "imagem_path" in result
        assert "obs" in result
        assert result["obs"] == "O gráfico está sendo exibido ao usuário na interface"


class TestPreverNecessidadeManutencaoTool:
    """Tests for maintenance prediction tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = PreverNecessidadeManutencaoTool()
        assert tool is not None
        assert tool.function_name == "prever_necessidade_manutencao"
    
    @patch('src.large_language_model.tools.prever_necessidade_manutencao_tool.Equipamento')
    def test_prever_manutencao_equipamento_not_found(self, mock_equipamento):
        """Test prediction when equipment doesn't exist."""
        mock_equipamento.get_from_id.return_value = None
        result = prever_necessidade_manutencao(equipamento_id=999)
        assert "não encontrado" in result
    
    @patch('src.large_language_model.tools.prever_necessidade_manutencao_tool.Equipamento')
    def test_prever_manutencao_no_sensors(self, mock_equipamento):
        """Test prediction when equipment has no sensors."""
        mock_equip = Mock()
        mock_equip.nome = "Equipamento Teste"
        mock_equip.sensores = []
        mock_equipamento.get_from_id.return_value = mock_equip
        
        result = prever_necessidade_manutencao(equipamento_id=1)
        assert "não possui sensores" in result
    
    @patch('src.large_language_model.tools.prever_necessidade_manutencao_tool.carregar_modelo_legado')
    @patch('src.large_language_model.tools.prever_necessidade_manutencao_tool.Equipamento')
    def test_prever_manutencao_no_model(self, mock_equipamento, mock_carregar_modelo):
        """Test prediction when ML model doesn't exist."""
        mock_equip = Mock()
        mock_equip.nome = "Equipamento Teste"
        mock_equip.sensores = [Mock()]
        mock_equipamento.get_from_id.return_value = mock_equip
        
        mock_carregar_modelo.side_effect = FileNotFoundError("Model not found")
        
        result = prever_necessidade_manutencao(equipamento_id=1)
        assert "Modelo de predição não encontrado" in result


class TestPreverManutencaoPorValoresTool:
    """Tests for maintenance prediction by values tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = PreverManutencaoPorValoresTool()
        assert tool is not None
        assert tool.function_name == "prever_manutencao_por_valores"
    
    def test_tool_has_docstring(self):
        """Test that the function has a docstring."""
        tool = PreverManutencaoPorValoresTool()
        assert tool.function_declaration.__doc__ is not None
        assert len(tool.function_declaration.__doc__.strip()) > 0
    
    @patch('src.large_language_model.tools.prever_por_valores_tool.carregar_modelo_legado')
    def test_prever_por_valores_no_model(self, mock_carregar_modelo):
        """Test prediction when ML model doesn't exist."""
        mock_carregar_modelo.side_effect = FileNotFoundError("Model not found")
        
        result = prever_manutencao_por_valores(lux=15.0, temperatura=25.0, vibracao=0.5)
        assert "Modelo de predição não encontrado" in result
    
    @patch('src.large_language_model.tools.prever_por_valores_tool.realizar_previsao')
    @patch('src.large_language_model.tools.prever_por_valores_tool.carregar_modelo_legado')
    def test_prever_por_valores_success(self, mock_carregar_modelo, mock_realizar_previsao):
        """Test successful prediction with values."""
        mock_model = Mock()
        mock_carregar_modelo.return_value = mock_model
        
        mock_realizar_previsao.return_value = {
            'predicao': 1,
            'probabilidade_manutencao': 0.75,
            'probabilidade_sem_manutencao': 0.25,
            'tem_proba': True,
            'dados_entrada': {
                'lux': 15.0,
                'temperatura': 25.0,
                'vibracao': 0.5
            }
        }
        
        result = prever_manutencao_por_valores(lux=15.0, temperatura=25.0, vibracao=0.5)
        
        assert "MANUTENÇÃO RECOMENDADA" in result
        assert "75.0%" in result or "75%" in result
        assert "Luminosidade: 15.00" in result
        assert "Temperatura: 25.00" in result
        assert "Vibração: 0.50" in result
    
    @patch('src.large_language_model.tools.prever_por_valores_tool.realizar_previsao')
    @patch('src.large_language_model.tools.prever_por_valores_tool.carregar_modelo_legado')
    def test_prever_por_valores_no_maintenance(self, mock_carregar_modelo, mock_realizar_previsao):
        """Test prediction indicating no maintenance needed."""
        mock_model = Mock()
        mock_carregar_modelo.return_value = mock_model
        
        mock_realizar_previsao.return_value = {
            'predicao': 0,
            'probabilidade_manutencao': 0.15,
            'probabilidade_sem_manutencao': 0.85,
            'tem_proba': True,
            'dados_entrada': {
                'lux': 10.0,
                'temperatura': 20.0,
                'vibracao': 0.3
            }
        }
        
        result = prever_manutencao_por_valores(lux=10.0, temperatura=20.0, vibracao=0.3)
        
        assert "CONDIÇÕES NORMAIS" in result
        assert "15.0%" in result or "15%" in result
    
    def test_call_chat_display(self):
        """Test chat display message."""
        tool = PreverManutencaoPorValoresTool()
        message = tool.call_chat_display()
        assert "🤖" in message or "Analisando" in message
    
    def test_call_result_display(self):
        """Test result display message."""
        tool = PreverManutencaoPorValoresTool()
        result = "Test result"
        display = tool.call_result_display(result)
        assert result in display


class TestObterLeituraMaisRecenteSensorTool:
    """Tests for getting most recent sensor reading tool."""
    
    def test_tool_instantiation(self):
        """Test that the tool can be instantiated."""
        tool = ObterLeituraMaisRecenteSensorTool()
        assert tool is not None
        assert tool.function_name == "obter_leitura_mais_recente_sensor"
    
    def test_tool_has_docstring(self):
        """Test that the function has a docstring."""
        tool = ObterLeituraMaisRecenteSensorTool()
        assert tool.function_declaration.__doc__ is not None
        assert len(tool.function_declaration.__doc__.strip()) > 0
    
    def test_obter_leitura_sensor_not_found(self):
        """Test getting reading when sensor doesn't exist."""
        result = obter_leitura_mais_recente_sensor(sensor_id=99999)
        assert "não encontrado" in result.lower() or "erro" in result.lower()
    
    @patch('src.large_language_model.tools.obter_leitura_mais_recente_sensor_tool.Database.get_session')
    def test_obter_leitura_no_readings(self, mock_get_session):
        """Test getting reading when no readings exist."""
        # Mock sensor exists
        mock_sensor = Mock()
        mock_sensor.id = 1
        mock_sensor.nome = "Test Sensor"
        mock_sensor.tipo_sensor = Mock()
        mock_sensor.tipo_sensor.tipo = "Temperatura (°C)"
        mock_sensor.equipamento = None
        
        # Mock session to return sensor but no readings
        mock_session = MagicMock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        
        def session_query_side_effect(model):
            query_mock = Mock()
            if model.__name__ == 'Sensor':
                query_mock.options.return_value.filter.return_value.one_or_none.return_value = mock_sensor
            else:  # LeituraSensor
                query_mock.filter.return_value.order_by.return_value.first.return_value = None
            return query_mock
        
        mock_session.query.side_effect = session_query_side_effect
        mock_get_session.return_value = mock_session
        
        result = obter_leitura_mais_recente_sensor(sensor_id=1)
        assert "nenhuma leitura" in result.lower() or "não encontrada" in result.lower()
    
    @patch('src.large_language_model.tools.obter_leitura_mais_recente_sensor_tool.Database.get_session')
    def test_obter_leitura_with_reading(self, mock_get_session):
        """Test getting reading when reading exists."""
        # Mock sensor
        mock_sensor = Mock()
        mock_sensor.id = 1
        mock_sensor.nome = "Sensor Temperatura"
        mock_sensor.tipo_sensor = Mock()
        mock_sensor.tipo_sensor.tipo = "Temperatura (°C)"
        mock_sensor.equipamento = Mock()
        mock_sensor.equipamento.nome = "Equipamento 1"
        mock_sensor.equipamento.id = 1
        
        # Mock reading
        mock_leitura = Mock()
        mock_leitura.valor = 25.5
        mock_leitura.data_leitura = datetime.now() - timedelta(minutes=5)
        
        # Mock session
        mock_session = MagicMock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        
        def session_query_side_effect(model):
            query_mock = Mock()
            if model.__name__ == 'Sensor':
                query_mock.options.return_value.filter.return_value.one_or_none.return_value = mock_sensor
            else:  # LeituraSensor
                query_mock.filter.return_value.order_by.return_value.first.return_value = mock_leitura
            return query_mock
        
        mock_session.query.side_effect = session_query_side_effect
        mock_get_session.return_value = mock_session
        
        result = obter_leitura_mais_recente_sensor(sensor_id=1)
        
        assert "Leitura Mais Recente" in result
        assert "25.5" in result or "25.50" in result
        assert "Sensor Temperatura" in result
    
    def test_call_chat_display(self):
        """Test chat display message."""
        tool = ObterLeituraMaisRecenteSensorTool()
        message = tool.call_chat_display()
        assert "📡" in message or "Consultando" in message
    
    def test_call_result_display(self):
        """Test result display message."""
        tool = ObterLeituraMaisRecenteSensorTool()
        result = "Test result"
        display = tool.call_result_display(result)
        assert result in display


class TestToolsDiscovery:
    """Tests for automatic tool discovery."""
    
    def test_all_new_tools_are_discovered(self):
        """Test that all new tools are discovered by the dynamic import system."""
        from src.large_language_model.dynamic_tools import import_tools
        
        tools = import_tools()
        tool_names = list(tools.keys())
        
        # Check that all new tools are discovered
        expected_tools = [
            'ListarEquipamentosTool',
            'ListarSensoresTool',
            'AgendarManutencaoTool',
            'EnviarNotificacaoTool',
            'AnalisarDadosSensorTool',
            'GerarGraficoLeiturasTool',
            'PreverNecessidadeManutencaoTool',
            'PreverManutencaoPorValoresTool',
            'ObterLeituraMaisRecenteSensorTool'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} not discovered"
    
    def test_all_new_tools_have_proper_structure(self):
        """Test that all new tools follow the proper structure."""
        from src.large_language_model.dynamic_tools import import_tools
        from src.large_language_model.tipos_base.base_tools import BaseTool
        
        tools = import_tools()
        
        new_tool_names = [
            'ListarEquipamentosTool',
            'ListarSensoresTool',
            'AgendarManutencaoTool',
            'EnviarNotificacaoTool',
            'AnalisarDadosSensorTool',
            'GerarGraficoLeiturasTool',
            'PreverNecessidadeManutencaoTool',
            'PreverManutencaoPorValoresTool',
            'ObterLeituraMaisRecenteSensorTool'
        ]
        
        for tool_name in new_tool_names:
            if tool_name in tools:
                tool_class = tools[tool_name]
                
                # Test instantiation
                tool_instance = tool_class()
                
                # Test it's a BaseTool
                assert isinstance(tool_instance, BaseTool)
                
                # Test it has required methods
                assert hasattr(tool_instance, 'function_declaration')
                assert hasattr(tool_instance, 'call_chat_display')
                assert hasattr(tool_instance, 'call_result_display')
                
                # Test function has docstring
                assert tool_instance.function_declaration.__doc__ is not None
                assert len(tool_instance.function_declaration.__doc__.strip()) > 0
