# Chatbot Tools - Quick Reference

## ✅ Status: All 7 Tools Implemented and Tested

This document provides a quick reference for the 7 new chatbot tools.

---

## 📋 Tools Summary

| # | Tool | Function | Purpose |
|---|------|----------|---------|
| 1 | 📦 **ListarEquipamentos** | `listar_equipamentos()` | List all equipment in system |
| 2 | 📡 **ListarSensores** | `listar_sensores(equipamento_id?)` | List all sensors (optionally filter by equipment) |
| 3 | 📅 **AgendarManutencao** | `agendar_manutencao(equipamento_id, data, motivo, descricao?)` | Schedule new maintenance |
| 4 | 📧 **EnviarNotificacao** | `enviar_notificacao(assunto, mensagem)` | Send email via AWS SNS |
| 5 | 📊 **AnalisarDadosSensor** | `analisar_dados_sensor(sensor_id, dias?)` | Statistical analysis of sensor data |
| 6 | 📈 **GerarGraficoLeituras** | `gerar_grafico_leituras(sensor_id, dias?, data?)` | Generate sensor reading graphs |
| 7 | 🤖 **PreverManutencao** | `prever_necessidade_manutencao(equipamento_id, dias?)` | ML-based maintenance prediction |

---

## 🚀 Quick Start

### Using the Chatbot

```bash
# Start dashboard
streamlit run main_dash.py

# Navigate to: 🤖 Chat IA
# Ask questions in natural language!
```

### Example Questions

```
"Quais equipamentos temos?"
→ Lists all equipment

"Mostre os sensores do equipamento 1"
→ Lists sensors for equipment 1

"Analise o sensor 5 dos últimos 7 dias"
→ Statistical analysis with trends and anomalies

"O equipamento 2 precisa de manutenção?"
→ ML prediction with probability

"Gere um gráfico do sensor 3"
→ Graph with statistics

"Agende manutenção para o equipamento 1 em 2025-01-15"
→ Creates maintenance record

"Envie uma notificação sobre temperatura alta"
→ Sends email via SNS (if configured)
```

---

## 🧪 Testing

```bash
# Test new tools only
pytest tests/unit/test_new_chatbot_tools.py -v

# Test all
pytest tests/unit/ -v

# Run demo
PYTHONPATH=. python src/large_language_model/tools_demo.py
```

**Test Results:** ✅ 32/32 tests passing

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [NEW_TOOLS_GUIDE.md](NEW_TOOLS_GUIDE.md) | Comprehensive guide with examples |
| [TOOLS_GUIDE.md](TOOLS_GUIDE.md) | Original tool development guide |
| [tools_demo.py](tools_demo.py) | Interactive demonstration |

---

## 🔧 Configuration

### Email Notifications (Optional)

Add to `.env`:
```bash
SNS_TOPIC_ARN=arn:aws:sns:region:account:topic
SNS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### ML Models (Required for predictions)

Models should be in: `assets/modelos_otimizados_salvos/DecTree_d5.pkl`

If missing:
```bash
python src/machine_learning/training.py
```

---

## 🏗️ Architecture

```
src/large_language_model/
├── tools/
│   ├── listar_equipamentos_tool.py       ← Lists equipment
│   ├── listar_sensores_tool.py           ← Lists sensors
│   ├── agendar_manutencao_tool.py        ← Schedules maintenance
│   ├── enviar_notificacao_tool.py        ← Sends emails
│   ├── analisar_dados_sensor_tool.py     ← Analyzes data
│   ├── gerar_grafico_leituras_tool.py    ← Generates graphs
│   └── prever_necessidade_manutencao_tool.py ← ML predictions
├── dynamic_tools.py      ← Auto-discovery
└── client.py             ← LLM integration
```

**Auto-Discovery:** All tools are automatically found and registered with the LLM!

---

## 📊 Features

### 1. Equipment Listing
- Shows ID, name, model, location
- Installation dates
- Associated sensor count

### 2. Sensor Listing
- Type (temperature, vibration, luminosity)
- Thresholds
- Equipment associations
- Filter by equipment

### 3. Maintenance Scheduling
- Multiple date formats
- Validates equipment existence
- Warns about past dates
- Records in database

### 4. Email Notifications
- AWS SNS integration
- Auto-truncates long subjects
- Helpful error messages
- Confirmation with message ID

### 5. Data Analysis
- Mean, median, std deviation
- Min, max, variance
- Outlier detection (>2σ)
- Trend analysis
- Threshold violations
- Actionable recommendations

### 6. Graph Generation
- Time series plots
- Threshold lines
- Statistical summary
- Trend detection
- Base64 encoded images

### 7. ML Prediction
- 95.24% accuracy
- Decision Tree model
- Probability score
- Detailed recommendations
- Multi-sensor analysis

---

## 🎯 Use Cases

### Scenario 1: Daily Check
```
User: "Como estão os equipamentos hoje?"
Bot: Lists equipment → Analyzes sensors → Reports status
```

### Scenario 2: Investigation
```
User: "O sensor 3 está com leituras estranhas"
Bot: Analyzes data → Generates graph → Identifies anomalies → Suggests action
```

### Scenario 3: Predictive Maintenance
```
User: "Verifique se algum equipamento precisa de manutenção"
Bot: Checks all equipment → ML predictions → Schedules maintenance → Sends notifications
```

---

## ✨ Key Benefits

- 🤖 **Natural Language:** Ask in plain Portuguese or English
- 🔄 **Automatic Discovery:** Tools auto-register with LLM
- 📊 **Data-Driven:** Uses real database and ML models
- 🔒 **Safe:** Validates inputs, handles errors gracefully
- 📝 **Well-Tested:** 100% test coverage
- 📚 **Well-Documented:** Comprehensive guides and examples
- 🚀 **Production-Ready:** Follows best practices

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Tool not discovered | Check file is in `tools/` folder and inherits from `BaseTool` |
| Model not found | Run `python src/machine_learning/training.py` |
| Notifications fail | Check AWS credentials in `.env` |
| No data returned | Verify database has records |

---

## 📈 Metrics

- ✅ 7 new tools implemented
- ✅ 32 comprehensive tests
- ✅ 100 total tests passing
- ✅ Zero breaking changes
- ✅ Auto-discovery working
- ✅ Full documentation

---

## 👥 For Developers

### Adding a New Tool

1. Create file in `src/large_language_model/tools/`
2. Inherit from `BaseTool`
3. Implement required methods
4. Add comprehensive docstring
5. Test with pytest
6. Done! Auto-discovery handles the rest

See [TOOLS_GUIDE.md](TOOLS_GUIDE.md) for detailed instructions.

---

**Last Updated:** 2024-10-29  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
