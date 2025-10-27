# 🧪 Guia de Testes - FIAP Sprint 4 Reply

## 📋 Índice
- [Instalação](#instalação)
- [Como Rodar os Testes](#como-rodar-os-testes)
- [Tipos de Testes](#tipos-de-testes)
- [Verificação de Memory Leaks](#verificação-de-memory-leaks)
- [Interpretando Resultados](#interpretando-resultados)
- [Bugs Encontrados](#bugs-encontrados)

## 🚀 Instalação

### 1. Criar Ambiente Virtual

```bash
# No Windows
python -m venv .venv
.venv\Scripts\activate

# No Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

As dependências de teste incluem:
- `pytest` - Framework de testes
- `pytest-cov` - Cobertura de código
- `pytest-mock` - Mocks e patches
- `pytest-asyncio` - Testes assíncronos
- `memory-profiler` - Análise de memória
- `httpx` - Cliente HTTP para testes de API
- `objgraph` - Visualização de objetos em memória

## 🏃 Como Rodar os Testes

### Opção 1: Usar o Script Helper (Recomendado)

```bash
# No Linux/Mac
./tests/run_tests.sh [opção]

# No Windows
tests\run_tests.bat [opção]
```

**Opções disponíveis:**
- `all` - Roda todos os testes (padrão)
- `unit` - Apenas testes unitários
- `integration` - Apenas testes de integração
- `memory` - Apenas testes de memory leak
- `coverage` - Testes com relatório de cobertura
- `quick` - Testes rápidos (pula testes lentos)
- `summary` - Mostra sumário dos testes
- `help` - Mostra ajuda

**Exemplos:**
```bash
./tests/run_tests.sh unit      # Apenas testes unitários
./tests/run_tests.sh coverage  # Com cobertura de código
./tests/run_tests.sh quick     # Testes rápidos
```

### Opção 2: Comandos pytest Diretos

### Rodar Todos os Testes

```bash
pytest
```

### Rodar com Saída Detalhada

```bash
pytest -v
```

### Rodar Testes Específicos

```bash
# Apenas testes unitários
pytest tests/unit/

# Apenas testes de integração
pytest tests/integration/

# Apenas testes de memória
pytest tests/memory/

# Um arquivo específico
pytest tests/unit/test_database.py

# Uma classe específica
pytest tests/unit/test_database.py::TestDatabaseInitialization

# Um teste específico
pytest tests/unit/test_database.py::TestDatabaseInitialization::test_init_sqlite_default_path
```

### Rodar com Cobertura de Código

```bash
# Gera relatório de cobertura
pytest --cov=src --cov-report=html

# Ver relatório
# Abra o arquivo htmlcov/index.html no navegador
```

### Rodar Testes Rápidos (Pular Testes Lentos)

```bash
pytest -m "not slow"
```

## 📊 Tipos de Testes

### Testes Unitários (`tests/unit/`)

Testam funções e classes individuais isoladamente.

**Exemplos:**
- `test_database.py` - Testa o módulo Database
- `test_validation_and_bugs.py` - Testa validações e documenta bugs

### Testes de Integração (`tests/integration/`)

Testam interações entre componentes.

**Exemplos:**
- `test_api.py` - Testa endpoints da API FastAPI

### Testes de Memória (`tests/memory/`)

Verificam vazamentos de memória (memory leaks).

**Exemplos:**
- `test_memory_leaks.py` - Detecta vazamentos no dashboard e banco de dados

## 🔍 Verificação de Memory Leaks

### Método 1: Testes Automáticos com pytest

```bash
# Rodar testes de memória
pytest tests/memory/ -v
```

Os testes verificam:
- ✅ Sessões de banco de dados são fechadas
- ✅ Conexões não vazam em exceções
- ✅ Gráficos Plotly não acumulam em cache
- ✅ Operações repetidas mantêm memória estável

### Método 2: Memory Profiler Manual

Para análise mais detalhada, use o memory_profiler:

```bash
# Instalar (já incluído em requirements.txt)
pip install memory-profiler

# Rodar com profiling
python -m memory_profiler seu_script.py
```

**Exemplo de uso em código:**

```python
from memory_profiler import profile

@profile
def minha_funcao():
    # Seu código aqui
    dados = [i for i in range(1000000)]
    return dados
```

### Método 3: Tracemalloc (Python Built-in)

```python
import tracemalloc

# Iniciar rastreamento
tracemalloc.start()

# Snapshot inicial
snapshot1 = tracemalloc.take_snapshot()

# Execute seu código aqui
# ...

# Snapshot final
snapshot2 = tracemalloc.take_snapshot()

# Comparar
stats = snapshot2.compare_to(snapshot1, 'lineno')

# Ver top 10 crescimentos
for stat in stats[:10]:
    print(stat)

tracemalloc.stop()
```

### Método 4: Monitoramento em Produção

Use `psutil` para monitorar em tempo real:

```python
import psutil
import os

process = psutil.Process(os.getpid())

# Memória em MB
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Uso de memória: {memory_mb:.2f} MB")
```

## 📈 Interpretando Resultados

### Pytest - Códigos de Status

- ✅ `.` (ponto) - Teste passou
- ❌ `F` - Teste falhou
- ⚠️ `s` - Teste pulado (skip)
- ⏭️ `x` - Falha esperada (xfail)

### Cobertura de Código

- **>= 80%** - ✅ Boa cobertura
- **60-80%** - ⚠️ Cobertura aceitável
- **< 60%** - ❌ Cobertura insuficiente

### Memory Leaks

**Crescimento Aceitável:**
- Operações únicas: < 1MB
- Operações repetidas (100x): < 5MB

**Sinais de Vazamento:**
- ❌ Crescimento linear com operações
- ❌ Memória não é liberada após gc.collect()
- ❌ File descriptors aumentam continuamente

## 🐛 Bugs Encontrados

### 🔴 CRÍTICO - Thread Daemon na API

**Arquivo:** `src/api/api_basica.py` (linha 60)

**Problema:**
```python
def inciar_api_thread_paralelo():
    api_thread = threading.Thread(target=iniciar_api, daemon=True)
    api_thread.start()
```

**Impacto:**
- Thread daemon é finalizada abruptamente quando o programa termina
- Conexões de banco podem não ser fechadas
- Requisições podem ser interrompidas
- Dados podem ser corrompidos

**Recomendação:**
```python
# Implementar shutdown gracioso
import atexit
import threading

_api_thread = None
_shutdown_event = threading.Event()

def shutdown_api():
    _shutdown_event.set()
    if _api_thread:
        _api_thread.join(timeout=5)

atexit.register(shutdown_api)
```

### 🟡 MÉDIO - Estado Global no Database

**Arquivo:** `src/database/tipos_base/database.py`

**Problema:**
```python
class Database:
    engine: Engine  # Variável de classe (compartilhada)
    session: sessionmaker  # Variável de classe (compartilhada)
```

**Impacto:**
- Em ambientes multi-threaded pode causar race conditions
- Múltiplas inicializações não fecham engine antigo
- Possível vazamento de conexões

**Recomendação:**
- Usar context managers para engine
- Implementar singleton pattern adequado
- Fechar engine antigo antes de criar novo

### 🟡 MÉDIO - Parsing de Variáveis Booleanas

**Arquivos:** `src/dashboard/main.py`, `src/api/api_basica.py`

**Problema:**
```python
sql_lite = str(os.environ.get("SQL_LITE", 'false')).lower() == "true"
```

**Impacto:**
- Apenas reconhece "true" (case-insensitive)
- Valores como "1", "yes", "on" são tratados como False
- Pode confundir usuários

**Recomendação:**
```python
def parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).lower() in ('true', '1', 'yes', 'on')
```

### 🟡 MÉDIO - Handlers de Log Acumulam

**Arquivo:** `src/logger/config.py`

**Problema:**
- Múltiplas chamadas a `configurar_logger()` podem adicionar handlers duplicados
- Handlers não são limpos entre chamadas

**Impacto:**
- Mensagens de log duplicadas
- Vazamento de file descriptors
- Arquivos de log não fechados

**Recomendação:**
```python
def configurar_logger(filename):
    logger = logging.getLogger()
    
    # Limpar handlers existentes
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # Adicionar novo handler
    handler = logging.FileHandler(filename)
    logger.addHandler(handler)
```

### 🟢 BAIXO - Validação de Path no SQLite

**Arquivo:** `src/database/tipos_base/database.py`

**Problema:**
- Não valida caminhos de arquivo para SQLite
- Possível path injection (baixo risco em uso normal)

**Recomendação:**
- Validar que o path está dentro de um diretório esperado
- Rejeitar paths absolutos ou com `..`

### 🟢 BAIXO - Falta Validação de Entrada

**Geral**

**Problema:**
- Várias funções não validam tipos de entrada
- Valores None podem causar comportamento inesperado

**Recomendação:**
- Adicionar type hints
- Validar parâmetros no início das funções
- Usar Pydantic para validação

## 🎯 Próximos Passos

1. ✅ Corrigir bugs críticos (thread daemon)
2. ✅ Adicionar validação de entrada
3. ✅ Implementar shutdown gracioso
4. ✅ Melhorar gerenciamento de recursos
5. ✅ Adicionar mais testes de integração
6. ✅ Configurar CI/CD para rodar testes automaticamente

## 📞 Suporte

Se tiver dúvidas sobre os testes:
1. Leia este documento completo
2. Verifique os comentários nos arquivos de teste
3. Execute `pytest -h` para ver todas as opções

## 📚 Recursos Adicionais

