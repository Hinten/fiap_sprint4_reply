# Sistema de Gerenciamento de Modelos ML

Este documento descreve as otimizações implementadas no sistema de treinamento e previsão de modelos de machine learning.

## 📋 Visão Geral

O sistema foi otimizado para:
1. **Cachear** o carregamento de dados para evitar reprocessamento
2. **Comparar** os top 5 modelos treinados
3. **Salvar** modelos seletivamente com metadados
4. **Gerenciar** modelos salvos através de um registro persistente
5. **Selecionar** e usar modelos salvos para previsões

## 🎯 Funcionalidades Implementadas

### 1. Cache de Dados (`train_model_view.py`)

```python
@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def load_sensor_data():
    """Carrega dados dos sensores com cache para evitar recarregamentos."""
    return get_dataframe_leituras_sensores()
```

**Benefícios:**
- Reduz significativamente o tempo de carregamento após primeiro acesso
- Cache expira após 1 hora (configurável)
- Melhora experiência do usuário

### 2. Comparação de Top 5 Modelos

O sistema agora treina e compara os 5 melhores modelos automaticamente:

```python
# Seleciona top 5 ao invés de apenas 1
top_models = s.compare_models(n_select=5, sort=metrica, fold=5, turbo=turbo)
```

**Visualizações:**
- Tabela completa com todas as métricas
- Tabela filtrada com apenas top 5
- Gráfico de barras comparativo
- Métricas individuais por modelo

### 3. Salvamento Seletivo de Modelos

Cada um dos top 5 modelos pode ser salvo individualmente:

**Interface:**
- Expander por modelo com informações detalhadas
- Campo de nome personalizável (com timestamp padrão)
- Campo de notas/descrição
- Botão de salvamento individual
- Validação de nomes duplicados

**Metadados Salvos:**
- Tipo do modelo (RandomForest, LogisticRegression, etc.)
- Métricas de performance (Accuracy, AUC, F1, etc.)
- Data e hora do salvamento
- Notas/descrição do usuário

### 4. Sistema de Registry (`model_store.py`)

Módulo centralizado para gerenciar modelos:

```python
from src.utils.model_store import (
    save_model,      # Salva modelo com metadados
    load_model,      # Carrega modelo por nome
    list_models,     # Lista todos os modelos
    get_models_summary,  # Resumo formatado
    delete_model     # Remove modelo
)
```

**Estrutura do Registry (`registry.json`):**

```json
{
  "nome_do_modelo": {
    "path": "modelos_salvos/nome_do_modelo.pkl",
    "metadata": {
      "accuracy": 0.92,
      "precision": 0.90,
      "model_type": "RandomForest",
      "description": "Descrição do modelo"
    },
    "saved_at": "2025-10-29T19:39:21.040921"
  }
}
```

**Características:**
- Thread-safe (locks para operações concorrentes)
- Salvamento atômico (arquivo temporário + rename)
- Validação de nomes duplicados
- Metadados extensíveis

### 5. Seleção de Modelos para Previsão (`manual.py`)

Interface melhorada para usar modelos salvos:

**Recursos:**
- Lista modelos do registry com metadados
- Tabela interativa com informações (tipo, métricas, data)
- Selectbox para escolher modelo
- Detalhes expandíveis do modelo selecionado
- Fallback para método legado (pasta modelos_salvos)

**UI Aprimorada:**
- Layout em 3 colunas para inputs
- Ícones nos campos (💡 Lux, 🌡️ Temperatura, 📳 Vibração)
- Exibição de probabilidades (quando disponível)
- Mensagens de erro claras
- Botão primário destacado

## 🚀 Como Usar

### Treinar e Salvar Modelos

1. Acesse o dashboard: `streamlit run main_dash.py`
2. Navegue para a página **"Train Model"**
3. Configure os parâmetros de treinamento
4. Clique em **"Treinar e comparar modelos"**
5. Aguarde o treinamento (pode demorar alguns minutos)
6. Veja a comparação dos top 5 modelos
7. Expanda cada modelo e clique em **"💾 Salvar"**
8. Personalize o nome e adicione descrição
9. Confirme o salvamento

### Usar Modelos Salvos para Previsão

1. Navegue para **"Classificador Manual"**
2. Veja a tabela de modelos disponíveis
3. Selecione um modelo no dropdown
4. (Opcional) Expanda os detalhes do modelo
5. Insira os valores dos sensores (Lux, Temperatura, Vibração)
6. Clique em **"🔮 Fazer Previsão"**
7. Veja o resultado e probabilidades

### Programaticamente

```python
from src.utils.model_store import save_model, load_model

# Salvar modelo
metadata = {
    "accuracy": 0.95,
    "model_type": "GradientBoosting",
    "description": "Modelo otimizado para produção"
}
save_model(trained_model, "modelo_producao_v1", metadata)

# Carregar modelo
model = load_model("modelo_producao_v1")
prediction = model.predict([[15.0, 14.0, 0.5]])
```

## 📊 Demonstração

Execute o script de demonstração para ver o sistema em ação:

```bash
python demo_model_system.py
```

Este script irá:
1. Salvar 3 modelos de exemplo
2. Listar todos os modelos com metadados
3. Carregar um modelo e fazer previsões
4. Demonstrar diferentes cenários de sensores

## 🧪 Testes

### Executar Testes Unitários

```bash
# Apenas testes do model_store
python -m pytest tests/unit/test_model_store.py -v

# Todos os testes unitários
python -m pytest tests/unit/ -v
```

### Executar Testes de Integração

```bash
# Testes do workflow completo
python -m pytest tests/integration/test_model_workflow.py -v

# Todos os testes de integração
python -m pytest tests/integration/ -v
```

### Executar Todos os Testes

```bash
python -m pytest tests/ -v
```

**Cobertura Atual:**
- Testes passando: > 270
- Novos testes unitários: 13 (model_store)
- Novos testes de integração: 3 (workflow)
- Testes existentes: mantidos sem regressões

## 📁 Estrutura de Arquivos

```
src/
├── utils/
│   └── model_store.py          # Sistema de gerenciamento de modelos
├── dashboard/
│   └── machine_learning/
│       ├── train_model_view.py # View otimizada para treinamento
│       └── manual.py           # View otimizada para previsão
└── machine_learning/
    └── modelos_salvos/         # Diretório de modelos
        ├── registry.json       # Registro de modelos
        └── *.pkl               # Arquivos de modelos

tests/
├── unit/
│   └── test_model_store.py     # Testes unitários
└── integration/
    └── test_model_workflow.py  # Testes de integração

demo_model_system.py            # Script de demonstração
```

## 🔧 Configuração

### Diretório de Modelos

Por padrão, os modelos são salvos em:
```
src/machine_learning/modelos_salvos/
```

Para alterar, modifique a constante em `src/utils/model_store.py`:
```python
MODELS_DIR = Path("seu/caminho/customizado")
```

### Cache de Dados

O TTL (Time To Live) do cache é de 3600 segundos (1 hora). Para alterar:
```python
@st.cache_data(ttl=7200)  # 2 horas
def load_sensor_data():
    ...
```

## 🛡️ Segurança

- ✅ Validação de nomes de modelos
- ✅ Salvamento atômico de registry (evita corrupção)
- ✅ Thread-safe operations
- ✅ Tratamento de erros robusto
- ✅ Validação de tipos e valores

## 🚨 Troubleshooting

### Modelo não aparece na lista

1. Verifique se o registry.json existe
2. Verifique se o arquivo .pkl foi criado
3. Execute: `python -c "from src.utils.model_store import list_models; print(list_models())"`

### Erro ao carregar modelo

1. Verifique se o nome está correto
2. Verifique se o arquivo existe no caminho especificado
3. Tente recarregar a página (limpa cache do Streamlit)

### Registry corrompido

O sistema é robusto a registros corrompidos e retornará um dicionário vazio. Para resetar:
```bash
rm src/machine_learning/modelos_salvos/registry.json
```

## 📝 Notas Técnicas

### Compatibilidade

- ✅ Compatível com modelos PyCaret
- ✅ Compatível com modelos scikit-learn
- ✅ Suporta formatos .pkl e .joblib
- ✅ Mantém compatibilidade com método legado

### Performance

- Cache de dados melhora significativamente tempo de carregamento em acessos subsequentes
- Registry JSON é leve e rápido para leitura/escrita
- Salvamento atômico previne race conditions
- Thread-safe para ambientes multi-usuário

## 🎓 Melhores Práticas

1. **Nomeação de Modelos**: Use nomes descritivos com versão (ex: `rf_v1_20241029`)
2. **Metadados**: Sempre inclua pelo menos tipo e métrica principal
3. **Descrição**: Documente o que diferencia este modelo
4. **Limpeza**: Remova modelos antigos periodicamente
5. **Backup**: Mantenha backup do registry.json

## 🔗 Referências

- [PyCaret Documentation](https://pycaret.org/)
- [Streamlit Caching](https://docs.streamlit.io/library/advanced-features/caching)
- [Joblib Persistence](https://joblib.readthedocs.io/en/latest/persistence.html)

## 📞 Suporte

Para questões ou problemas:
1. Verifique este README
2. Execute `python demo_model_system.py` para validar instalação
3. Execute os testes: `python -m pytest tests/ -v`
4. Abra uma issue no repositório
