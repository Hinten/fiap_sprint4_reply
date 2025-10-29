# Guia de Desenvolvimento de Tools para o Assistente de IA

Este guia explica como criar novas ferramentas (tools) para estender as capacidades do assistente de IA generativo.

## 📋 Índice

1. [O que são Tools?](#o-que-são-tools)
2. [Arquitetura das Tools](#arquitetura-das-tools)
3. [Como Criar uma Nova Tool](#como-criar-uma-nova-tool)
4. [Exemplos de Tools](#exemplos-de-tools)
5. [Boas Práticas](#boas-práticas)
6. [Debugging e Testes](#debugging-e-testes)

---

## O que são Tools?

**Tools** (ferramentas) são funções Python que o modelo de linguagem generativa (Google Gemini) pode chamar automaticamente durante uma conversa para:

- 🔍 **Buscar dados reais** do banco de dados (sensores, equipamentos, leituras)
- 📊 **Calcular métricas** e estatísticas
- 🔔 **Executar ações** no sistema
- 📈 **Gerar relatórios** ou análises
- 🌐 **Consultar APIs externas**

Quando o usuário faz uma pergunta, o modelo decide automaticamente se precisa chamar uma ou mais tools para responder de forma precisa e com dados reais.

---

## Arquitetura das Tools

### Estrutura de Diretórios

```
src/large_language_model/
├── tipos_base/
│   └── base_tools.py          # Classe abstrata BaseTool
├── tools/
│   ├── __init__.py            # Documentação e instruções
│   ├── datetime_tool.py       # Tool de exemplo
│   └── sua_tool.py            # Sua nova tool aqui!
├── dynamic_tools.py           # Sistema de descoberta automática
└── client.py                  # Cliente que registra as tools
```

### Como Funciona

1. **Descoberta Automática**: O sistema varre a pasta `tools/` e encontra todas as classes que herdam de `BaseTool`
2. **Registro**: As tools são automaticamente registradas no cliente do Google Gemini
3. **Declaração**: Cada tool é convertida em uma `FunctionDeclaration` que o modelo entende
4. **Invocação**: Durante a conversa, o modelo pode chamar a tool passando os argumentos necessários
5. **Execução**: A tool executa, retorna o resultado, e o modelo usa essa informação na resposta

---

## Como Criar uma Nova Tool

### Passo 1: Defina a Função

Crie uma função Python com:
- **Nome descritivo** em snake_case
- **Docstring completa** explicando o que a função faz
- **Type hints** para todos os parâmetros e retorno
- **Parâmetros nomeados** (o modelo passa argumentos como kwargs)

```python
def get_ultima_leitura_sensor(sensor_id: int) -> str:
    """
    Retorna a última leitura de um sensor específico.
    
    Esta função busca no banco de dados a leitura mais recente
    do sensor especificado e retorna os valores de temperatura,
    vibração e luminosidade.
    
    :param sensor_id: ID do sensor a ser consultado
    :return: String formatada com os dados da última leitura
    """
    # Implementação aqui
    pass
```

**⚠️ IMPORTANTE**: A docstring é **obrigatória** e será mostrada ao modelo de IA para que ele saiba quando e como usar sua tool!

### Passo 2: Crie a Classe Tool

Crie uma classe que herda de `BaseTool` e implementa os métodos abstratos:

```python
from src.large_language_model.tipos_base.base_tools import BaseTool

class UltimaLeituraSensorTool(BaseTool):
    """
    Tool para consultar a última leitura de um sensor.
    """
    
    @property
    def function_declaration(self):
        """Retorna a função que será chamada pelo modelo."""
        return get_ultima_leitura_sensor
    
    def call_chat_display(self) -> str:
        """Mensagem mostrada quando a tool está sendo executada."""
        return "🔍 Consultando última leitura do sensor..."
    
    def call_result_display(self, result: str) -> str:
        """Mensagem mostrada com o resultado da execução."""
        return f"✅ Última leitura: {result}"
```

### Passo 3: Salve o Arquivo

Salve o arquivo em `src/large_language_model/tools/` com um nome descritivo:

```bash
src/large_language_model/tools/ultima_leitura_sensor_tool.py
```

**Pronto!** A tool será automaticamente descoberta e registrada na próxima execução.

---

## Exemplos de Tools

### Exemplo 1: Consulta Simples ao Banco

```python
# src/large_language_model/tools/equipamento_status_tool.py
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.equipamento import Equipamento

def get_equipamento_status(equipamento_id: int) -> str:
    """
    Retorna o status atual de um equipamento.
    
    :param equipamento_id: ID do equipamento
    :return: Status do equipamento (ativo, manutenção, parado)
    """
    equipamento = Equipamento.get_from_id(equipamento_id)
    if not equipamento:
        return f"Equipamento {equipamento_id} não encontrado."
    
    return f"Equipamento '{equipamento.nome}': Status {equipamento.status}"

class EquipamentoStatusTool(BaseTool):
    @property
    def function_declaration(self):
        return get_equipamento_status
    
    def call_chat_display(self) -> str:
        return "⚙️ Consultando status do equipamento..."
    
    def call_result_display(self, result: str) -> str:
        return f"✅ {result}"
```

### Exemplo 2: Cálculo de Métricas

```python
# src/large_language_model/tools/media_temperatura_tool.py
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.leitura_sensor import LeituraSensor
from datetime import datetime, timedelta
from sqlalchemy import func

def get_media_temperatura_ultimas_24h(sensor_id: int) -> str:
    """
    Calcula a média de temperatura de um sensor nas últimas 24 horas.
    
    :param sensor_id: ID do sensor a ser analisado
    :return: Média de temperatura em graus Celsius
    """
    limite = datetime.now() - timedelta(days=1)
    
    media = LeituraSensor.query.filter(
        LeituraSensor.sensor_id == sensor_id,
        LeituraSensor.data_leitura >= limite
    ).with_entities(
        func.avg(LeituraSensor.temperatura)
    ).scalar()
    
    if media is None:
        return "Sem leituras nas últimas 24 horas"
    
    return f"Média de temperatura: {media:.2f}°C"

class MediaTemperaturaTool(BaseTool):
    @property
    def function_declaration(self):
        return get_media_temperatura_ultimas_24h
    
    def call_chat_display(self) -> str:
        return "📊 Calculando média de temperatura..."
    
    def call_result_display(self, result: str) -> str:
        return f"✅ {result}"
```

### Exemplo 3: Tool com Múltiplos Parâmetros

```python
# src/large_language_model/tools/filtrar_alertas_tool.py
from src.large_language_model.tipos_base.base_tools import BaseTool
from src.database.models.manutencao_equipamento import ManutencaoEquipamento
from datetime import datetime, timedelta

def filtrar_alertas(
    dias: int = 7,
    tipo: str = "todos",
    urgente_apenas: bool = False
) -> str:
    """
    Filtra alertas de manutenção por período e tipo.
    
    :param dias: Número de dias para buscar alertas (padrão: 7)
    :param tipo: Tipo de alerta ('preventiva', 'corretiva', 'todos')
    :param urgente_apenas: Se True, retorna apenas alertas urgentes
    :return: Lista de alertas filtrados
    """
    limite = datetime.now() - timedelta(days=dias)
    
    query = ManutencaoEquipamento.query.filter(
        ManutencaoEquipamento.data_manutencao >= limite
    )
    
    if tipo != "todos":
        query = query.filter(ManutencaoEquipamento.tipo == tipo)
    
    if urgente_apenas:
        query = query.filter(ManutencaoEquipamento.urgente == True)
    
    alertas = query.all()
    
    if not alertas:
        return "Nenhum alerta encontrado com os filtros especificados."
    
    resultado = f"Encontrados {len(alertas)} alertas:\n"
    for alerta in alertas[:5]:  # Limite de 5 para não sobrecarregar
        resultado += f"- {alerta.equipamento.nome}: {alerta.descricao}\n"
    
    return resultado

class FiltrarAlertasTool(BaseTool):
    @property
    def function_declaration(self):
        return filtrar_alertas
    
    def call_chat_display(self) -> str:
        return "🔔 Filtrando alertas de manutenção..."
    
    def call_result_display(self, result: str) -> str:
        return f"📋 {result}"
```

---

## Boas Práticas

### ✅ Faça

1. **Docstrings Completas**: Descreva claramente o que a tool faz, parâmetros e retorno
2. **Type Hints**: Use sempre type hints para todos os parâmetros
3. **Tratamento de Erros**: Valide entradas e trate casos de erro graciosamente
4. **Retornos Descritivos**: Retorne strings legíveis e informativas
5. **Limite de Resultados**: Para consultas que podem retornar muitos dados, limite a quantidade
6. **Logging**: Use logging para debug quando apropriado
7. **Performance**: Otimize queries de banco de dados

### ❌ Evite

1. **Tools Muito Genéricas**: Seja específico - "get_temperatura_sensor" é melhor que "get_dados"
2. **Retornos Muito Grandes**: O modelo tem limite de contexto - retorne no máximo ~1000 palavras
3. **Operações Perigosas**: Evite deletar/modificar dados sem confirmação
4. **Código Bloqueante**: Evite operações muito lentas que travam o chat
5. **Dependências Externas Não Confiáveis**: Minimize chamadas a APIs externas não confiáveis

### 🎯 Nomenclatura

- **Função**: `get_`, `calculate_`, `list_`, `check_`, etc. + `_o_que_faz`
- **Classe**: Nome da função + `Tool` (ex: `GetTemperaturaTool`)
- **Arquivo**: nome_da_funcao + `_tool.py` (ex: `get_temperatura_tool.py`)

---

## Debugging e Testes

### Testar a Tool Isoladamente

```python
# Teste no Python REPL ou em um script
from src.large_language_model.tools.sua_tool import SuaTool

tool = SuaTool()
resultado = tool.execute(param1="valor1", param2="valor2")
print(resultado)
```

### Testar Descoberta Automática

```python
from src.large_language_model.dynamic_tools import import_tools

tools = import_tools(sort=True)
print(f"Tools descobertas: {list(tools.keys())}")
```

### Testar no Chat

1. Inicie o dashboard: `streamlit run main_dash.py`
2. Vá para "🤖 Chat IA"
3. Faça uma pergunta que deveria usar sua tool
4. Observe se o modelo chama a tool corretamente
5. Verifique a resposta e os logs

### Criar Testes Unitários

```python
# tests/unit/test_sua_tool.py
import pytest
from src.large_language_model.tools.sua_tool import SuaTool, sua_funcao

def test_sua_tool_instantiation():
    tool = SuaTool()
    assert tool is not None

def test_sua_funcao_retorna_string():
    resultado = sua_funcao(param="valor")
    assert isinstance(resultado, str)
    assert len(resultado) > 0

def test_sua_tool_execute():
    tool = SuaTool()
    resultado = tool.execute(param="valor")
    assert "esperado" in resultado
```

Execute os testes:
```bash
python -m pytest tests/unit/test_sua_tool.py -v
```

---

## Exemplos Práticos de Uso

Quando você cria uma tool, o modelo aprende automaticamente a usá-la. Por exemplo:

**Usuário**: "Qual é a temperatura do sensor 5?"  
**Modelo**: *chama `get_ultima_leitura_sensor(sensor_id=5)`*  
**Tool**: "Sensor 'MPU6050-001': 25.3°C, Vibração: 0.02g, Luminosidade: 450 lux"  
**Modelo**: "O sensor 5 está com temperatura de 25.3°C, que está dentro da faixa normal."

**Usuário**: "Houve alertas de temperatura alta esta semana?"  
**Modelo**: *chama `filtrar_alertas(dias=7, tipo="todos", urgente_apenas=False)`*  
**Tool**: "Encontrados 3 alertas: ..."  
**Modelo**: "Sim, houve 3 alertas esta semana. Os principais foram..."

---

## Recursos Adicionais

- **Documentação Google GenAI**: https://ai.google.dev/gemini-api/docs/function-calling
- **Código Base**: `src/large_language_model/tipos_base/base_tools.py`
- **Tool de Exemplo**: `src/large_language_model/tools/datetime_tool.py`
- **Testes de Referência**: `tests/unit/test_chat.py`

---

## Perguntas Frequentes

### P: Quantas tools posso criar?
**R**: Não há limite técnico, mas o modelo funciona melhor com 10-20 tools bem focadas do que 100 genéricas.

### P: As tools precisam retornar strings?
**R**: Sim, sempre retorne strings. O modelo trabalha com texto. Use formatação clara (JSON, listas, tabelas).

### P: Posso fazer tools que modificam o banco de dados?
**R**: Sim, mas com cuidado. Implemente confirmações e validações robustas.

### P: Como o modelo sabe qual tool usar?
**R**: O modelo analisa a docstring da função e decide com base no contexto da conversa.

### P: Posso ter tools que chamam outras tools?
**R**: Tecnicamente sim, mas não é recomendado. Deixe o modelo orquestrar as chamadas.

### P: E se a tool falhar?
**R**: Implemente try/except e retorne mensagens de erro amigáveis. O modelo vai incorporar isso na resposta.

---

**Pronto para começar?** Crie sua primeira tool seguindo os exemplos acima! 🚀
