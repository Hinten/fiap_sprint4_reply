# ML Prediction Module - Documentation

## Overview
This module provides reusable machine learning prediction functionality for equipment maintenance prediction. It can be used by both the Streamlit dashboard and LLM tools.

## Location
- **Module**: `src/ml/prediction.py`
- **Tools**: 
  - `src/large_language_model/tools/prever_necessidade_manutencao_tool.py` (equipment-based)
  - `src/large_language_model/tools/prever_por_valores_tool.py` (value-based)
- **Dashboard**: `src/dashboard/machine_learning/manual.py`

## Key Functions

### 1. `preparar_dados_para_previsao(lux, temp, vibracao)`
Prepares input data in the correct format for ML models.

**Parameters:**
- `lux` (float): Luminosity value (in lux or x10³)
- `temp` (float): Temperature in Celsius
- `vibracao` (float): Vibration level (typically 0-3)

**Returns:**
- `pd.DataFrame`: DataFrame with columns 'Lux (x10³)', 'Temperatura (°C)', 'Vibração'

**Example:**
```python
from src.ml.prediction import preparar_dados_para_previsao

df = preparar_dados_para_previsao(lux=15000, temp=25, vibracao=0.5)
# Returns DataFrame with shape (1, 3)
```

### 2. `carregar_modelo(nome_ou_caminho, usar_registry=True)`
Loads a ML model from registry or file system.

**Parameters:**
- `nome_ou_caminho` (Optional[str]): Model name or file path
- `usar_registry` (bool): Try loading from registry first

**Returns:**
- `Tuple[Any, Optional[Dict]]`: (model, metadata)

**Example:**
```python
from src.ml.prediction import carregar_modelo

# Load from registry
modelo, metadata = carregar_modelo("my_model")

# Load from file
modelo, _ = carregar_modelo("/path/to/model.pkl", usar_registry=False)
```

### 3. `realizar_previsao(modelo, lux, temp, vibracao)`
Performs prediction using a loaded model.

**Parameters:**
- `modelo`: Loaded ML model
- `lux` (float): Luminosity value
- `temp` (float): Temperature
- `vibracao` (float): Vibration level

**Returns:**
- `Dict[str, Any]`: Dictionary with:
  - `predicao` (int): 0 (no maintenance) or 1 (maintenance needed)
  - `probabilidade_manutencao` (float): Probability of needing maintenance (0-1)
  - `probabilidade_sem_manutencao` (float): Probability of not needing maintenance
  - `tem_proba` (bool): Whether model supports predict_proba
  - `dados_entrada` (dict): Input values used

**Example:**
```python
from src.ml.prediction import carregar_modelo, realizar_previsao

modelo, _ = carregar_modelo()
resultado = realizar_previsao(modelo, lux=15000, temp=25, vibracao=0.5)

if resultado['predicao'] == 1:
    print(f"Maintenance needed! Probability: {resultado['probabilidade_manutencao']:.2%}")
```

### 4. `carregar_modelo_e_realizar_previsao(lux, temp, vibracao, nome_ou_caminho_modelo=None, usar_registry=True)`
Complete workflow: loads model and performs prediction in one call.

**Parameters:**
- `lux` (float): Luminosity value
- `temp` (float): Temperature
- `vibracao` (float): Vibration level
- `nome_ou_caminho_modelo` (Optional[str]): Model name or path
- `usar_registry` (bool): Try loading from registry first

**Returns:**
- Same as `realizar_previsao()`

**Example:**
```python
from src.ml.prediction import carregar_modelo_e_realizar_previsao

# Simple one-line prediction
resultado = carregar_modelo_e_realizar_previsao(
    lux=15000.0,
    temp=25.0,
    vibracao=0.5
)

print(f"Prediction: {resultado['predicao']}")
print(f"Probability: {resultado['probabilidade_manutencao']:.2%}")
```

### 5. `obter_modelos_disponiveis()`
Lists all available models from registry and file system.

**Returns:**
- `Dict[str, Any]`: Dictionary with:
  - `registry`: List of models in registry
  - `legado`: List of legacy file-based models

**Example:**
```python
from src.ml.prediction import obter_modelos_disponiveis

modelos = obter_modelos_disponiveis()
print(f"Registry models: {len(modelos['registry'])}")
print(f"Legacy models: {len(modelos['legado'])}")

for modelo in modelos['legado']:
    print(f"  - {modelo['nome']}: {modelo['caminho']}")
```

## Tools

### PreverNecessidadeManutencaoTool
Predicts maintenance needs for a specific equipment by analyzing sensor readings.

**Usage in LLM:**
```python
from src.large_language_model.tools.prever_necessidade_manutencao_tool import (
    prever_necessidade_manutencao
)

# Analyze equipment with ID 1 using last 7 days of sensor data
resultado = prever_necessidade_manutencao(
    equipamento_id=1,
    dias_analise=7
)
print(resultado)
```

**Output:**
```
🤖 Predição de Manutenção - Machine Learning

📦 Equipamento: Bomba Hidráulica (ID: 1)
📅 Período Analisado: 7 dias
📡 Sensores Analisados: 3

📊 DADOS COLETADOS:
   • Sensor Lux (Lux (x10³)): 50 leitura(s)
   • Sensor Temp (Temperatura (°C)): 50 leitura(s)
   • Sensor Vibr (Vibração): 50 leitura(s)

📈 VALORES MÉDIOS DETECTADOS:
   • Luminosidade: 15234.56 lux
   • Temperatura: 28.34 °C
   • Vibração: 1.23

🎯 RESULTADO DA PREDIÇÃO:
   • Probabilidade de Necessidade de Manutenção: 75.5%
   • Status: ⚠️ MANUTENÇÃO RECOMENDADA

🔧 RECOMENDAÇÕES:
   • Agendar manutenção preventiva o mais breve possível
   • Verificar os sensores com leituras anormais
   • Monitorar o equipamento com maior frequência
   • Considerar inspeção técnica detalhada
```

### PreverManutencaoPorValoresTool
Predicts maintenance needs using direct sensor values (no equipment ID required).

**Usage in LLM:**
```python
from src.large_language_model.tools.prever_por_valores_tool import (
    prever_manutencao_por_valores
)

# Direct prediction with sensor values
resultado = prever_manutencao_por_valores(
    lux=20000.0,
    temperatura=35.0,
    vibracao=2.5
)
print(resultado)
```

**Output:**
```
🤖 Predição de Manutenção - Machine Learning

📊 VALORES DE ENTRADA:
   • Luminosidade: 20000.00 lux
   • Temperatura: 35.00 °C
   • Vibração: 2.50

🎯 RESULTADO DA PREDIÇÃO:
   • Probabilidade de Manutenção: 85.2%
   • Probabilidade Sem Manutenção: 14.8%
   • Status: ⚠️ MANUTENÇÃO RECOMENDADA

🔧 RECOMENDAÇÕES:
   • Os valores indicam necessidade de manutenção
   • Verificar se os valores estão dentro dos limites normais de operação
   • Considerar agendar manutenção preventiva
   • ⚠️ Vibração alta (2.50) - valor típico < 2.0

📝 Modelo: RandomForestClassifier
```

## Dashboard Integration

The dashboard (`src/dashboard/machine_learning/manual.py`) now uses the shared prediction module:

```python
from src.ml.prediction import realizar_previsao as realizar_previsao_ml

# In the dashboard code:
resultado = realizar_previsao_ml(modelo, lux, temp, vibracao)

if resultado['predicao'] == 1:
    st.error("⚠️ **Manutenção Necessária**")
else:
    st.success("✅ **Sem Necessidade de Manutenção**")

st.metric("Probabilidade - Com Manutenção", 
          f"{resultado['probabilidade_manutencao']:.2%}")
```

## Model Requirements

### Compatible Models
The module works with scikit-learn models that:
- Accept 3 features: Lux (x10³), Temperatura (°C), Vibração
- Are trained on normalized data (MinMaxScaler or similar)
- Support binary classification (0 = no maintenance, 1 = maintenance needed)
- Optionally support `predict_proba()` for probability estimates

### Model Locations
Models are searched in this order:
1. **Model Registry** (`src/machine_learning/modelos_salvos/registry.json`)
2. **Legacy Files**:
   - `src/machine_learning/modelos_salvos/*.pkl`
   - `src/machine_learning/modelos_salvos/*.joblib`
   - `assets/modelos_salvos/*.pkl`
   - `assets/modelos_salvos/*.joblib`

### Recommended Models
- `random_forest.joblib` (3 features, 66% accuracy)
- `logistic_regression.joblib` (3 features)
- `kneighbors.joblib` (3 features)
- `svc.joblib` (3 features)

**Note:** Avoid `DecTree_d5.pkl` in some directories as it may have 4 features instead of 3.

## Testing

### Unit Tests
Run tests for the ML prediction module:
```bash
pytest tests/unit/test_ml_prediction.py -v
```

**Test Coverage:**
- Data preparation (2 tests)
- Model loading (4 tests)
- Prediction execution (2 tests)
- Complete workflow (1 test)
- Model discovery (2 tests)

### Tool Tests
Run tests for the tools:
```bash
# Test equipment-based tool
pytest tests/unit/test_new_chatbot_tools.py::TestPreverNecessidadeManutencaoTool -v

# Test value-based tool
pytest tests/unit/test_new_chatbot_tools.py::TestPreverManutencaoPorValoresTool -v
```

### Integration Test
Run the comprehensive integration test:
```bash
python -c "
from src.ml.prediction import carregar_modelo_e_realizar_previsao
resultado = carregar_modelo_e_realizar_previsao(lux=15000, temp=25, vibracao=0.5)
print(f'Success! Prediction: {resultado[\"predicao\"]}')
"
```

## Error Handling

The module handles several error scenarios:
- **Model not found**: Returns FileNotFoundError with helpful message
- **Invalid input**: Validates data types and ranges
- **Model loading errors**: Catches and reports serialization issues
- **Prediction errors**: Reports issues with feature mismatch or model compatibility

## Performance

- **Model loading**: ~50-100ms (first time), cached thereafter
- **Prediction**: ~1-5ms per prediction
- **Memory**: ~10-50MB depending on model complexity

## Migration Guide

### From Old Tool to New Module

**Before:**
```python
# Old implementation with hardcoded paths and manual scaling
modelo_path = "assets/modelos_salvos/DecTree_d5.pkl"
modelo = joblib.load(modelo_path)
scaler = MinMaxScaler()
scaler.fit([[-40, 0, 0.1], [85, 3, 100000]])
features_scaled = scaler.transform([[temp, vibr, lux]])[0]
predicao = modelo.predict([features_scaled])[0]
```

**After:**
```python
# New implementation with shared module
from src.ml.prediction import carregar_modelo_e_realizar_previsao

resultado = carregar_modelo_e_realizar_previsao(
    lux=lux, temp=temp, vibracao=vibr
)
predicao = resultado['predicao']
probabilidade = resultado['probabilidade_manutencao']
```

## Troubleshooting

### "Model not found" error
1. Check if models exist: `obter_modelos_disponiveis()`
2. Verify model path or name
3. Ensure models are in correct directory

### "Wrong number of features" error
1. Ensure using 3-feature models (not 4 or 7)
2. Check model with `model.n_features_in_`
3. Use recommended models listed above

### "sklearn version mismatch" warning
- Can be safely ignored in most cases
- Models trained with sklearn 1.7.1, running on 1.4.2
- Predictions still work correctly

## Future Improvements
- Support for additional features (equipamento_id encoding)
- Model versioning and A/B testing
- Automatic model selection based on performance
- Real-time model retraining pipeline
- Support for more ML frameworks (TensorFlow, PyTorch)
