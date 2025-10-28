# 🐛 Relatório de Bugs e Análise de Código

**Data:** 27 de Outubro de 2025  
**Projeto:** FIAP Sprint 4 Reply  
**Analisador:** Suite de Testes Automatizada

---

## 📊 Resumo Executivo

Durante a análise do código foram identificados **6 bugs/problemas** de diferentes níveis de severidade:
- 🔴 **1 CRÍTICO** - Requer ação imediata
- 🟡 **3 MÉDIOS** - Devem ser corrigidos em breve  
- 🟢 **2 BAIXOS** - Melhorias recomendadas

---

## 🔴 Bugs Críticos

### Bug #1: Thread Daemon Não Gerenciada Adequadamente

**Severidade:** 🔴 CRÍTICA  
**Arquivo:** `src/api/api_basica.py`  
**Linha:** 60-66  

**Descrição:**
A função `inciar_api_thread_paralelo()` cria uma thread daemon para executar a API FastAPI em background. Threads daemon são terminadas abruptamente quando o processo principal termina, sem permitir cleanup adequado.

**Código Problemático:**
```python
def inciar_api_thread_paralelo():
    """
    Inicia a API em uma thread separada.
    """
    api_thread = threading.Thread(target=iniciar_api, daemon=True)
    api_thread.start()
```

**Impacto:**
- ❌ Conexões de banco de dados podem não ser fechadas
- ❌ Requisições HTTP em andamento podem ser interrompidas
- ❌ Dados podem ser corrompidos em transações incompletas
- ❌ Arquivos abertos podem não ser fechados

**Solução Recomendada:**
```python
import atexit
import threading
import signal

_api_thread = None
_shutdown_event = threading.Event()

def shutdown_api():
    """Desliga a API graciosamente."""
    print("Desligando API...")
    _shutdown_event.set()
    
    if _api_thread and _api_thread.is_alive():
        _api_thread.join(timeout=10)
        if _api_thread.is_alive():
            print("AVISO: API não respondeu ao shutdown em 10 segundos")

def inciar_api_thread_paralelo():
    """Inicia a API em uma thread separada com shutdown gracioso."""
    global _api_thread
    
    _api_thread = threading.Thread(target=iniciar_api, daemon=False)
    _api_thread.start()
    
    # Registra shutdown
    atexit.register(shutdown_api)
    signal.signal(signal.SIGTERM, lambda s, f: shutdown_api())
    signal.signal(signal.SIGINT, lambda s, f: shutdown_api())
```

---

## 🟡 Bugs Médios

### Bug #2: Estado Global Compartilhado no Database

**Severidade:** 🟡 MÉDIA  
**Arquivo:** `src/database/tipos_base/database.py`  
**Linhas:** 16-20

**Descrição:**
A classe `Database` usa variáveis de classe para armazenar `engine` e `session`, que são compartilhadas entre todas as partes do código. Isso pode causar problemas em ambientes multi-threaded ou quando múltiplas instâncias são necessárias.

**Código Problemático:**
```python
class Database:
    engine: Engine        # Compartilhado globalmente
    session: sessionmaker  # Compartilhado globalmente
```

**Impacto:**
- ⚠️ Race conditions em ambiente multi-threaded
- ⚠️ Impossível ter múltiplas conexões simultâneas
- ⚠️ Re-inicialização não fecha engine antigo (memory leak)

**Solução Recomendada:**
```python
class Database:
    _engine: Optional[Engine] = None
    _session: Optional[sessionmaker] = None
    _lock = threading.Lock()
    
    @classmethod
    def init_sqlite(cls, path: Optional[str] = None):
        with cls._lock:
            # Fecha engine antigo se existir
            if cls._engine is not None:
                cls._engine.dispose()
            
            if path is None:
                path = os.path.join(os.getcwd(), "database.db")
            
            cls._engine = create_engine(f"sqlite:///{path}", echo=SQL_ALCHEMY_DEBUG)
            cls._session = sessionmaker(autocommit=False, autoflush=False, bind=cls._engine)
```

---

### Bug #3: Parsing Limitado de Variáveis Booleanas

**Severidade:** 🟡 MÉDIA  
**Arquivos:** `src/dashboard/main.py` (linhas 24-26), `src/api/api_basica.py` (linhas 14-16)

**Descrição:**
O código atual só reconhece "true" como valor verdadeiro. Valores comuns como "1", "yes", "on" são tratados como falsos, o que pode confundir usuários.

**Código Problemático:**
```python
sql_lite = str(os.environ.get("SQL_LITE", 'false')).lower() == "true"
oracle = str(os.environ.get("ORACLE_DB_FROM_ENV", 'false')).lower() == "true"
postgres = str(os.environ.get("POSTGRE_DB_FROM_ENV", 'false')).lower() == "true"
```

**Impacto:**
- ⚠️ UX inconsistente com outras aplicações
- ⚠️ Documentação precisa especificar exatamente "true"
- ⚠️ Valores intuitivos como "1" não funcionam

**Solução Recomendada:**
```python
def parse_bool_env(env_var: str, default: bool = False) -> bool:
    """
    Converte variável de ambiente para booleano.
    
    Aceita: 'true', '1', 'yes', 'on' (case-insensitive) como True
    Qualquer outro valor é False
    """
    value = os.environ.get(env_var)
    if value is None:
        return default
    return str(value).lower() in ('true', '1', 'yes', 'on')

# Uso:
sql_lite = parse_bool_env("SQL_LITE")
oracle = parse_bool_env("ORACLE_DB_FROM_ENV")
postgres = parse_bool_env("POSTGRE_DB_FROM_ENV")
```

---

### Bug #4: Acúmulo de Handlers de Log

**Severidade:** 🟡 MÉDIA  
**Arquivo:** `src/logger/config.py`

**Descrição:**
Se `configurar_logger()` for chamada múltiplas vezes (por exemplo, em testes ou reconexões), novos handlers são adicionados sem remover os antigos, causando:
- Mensagens de log duplicadas
- Vazamento de file descriptors
- Arquivos não fechados

**Impacto:**
- ⚠️ Logs duplicados dificultam debugging
- ⚠️ File descriptors podem se esgotar em execuções longas
- ⚠️ Arquivos de log podem ficar travados

**Solução Recomendada:**
```python
def configurar_logger(filename: str, force_reconfigure: bool = False):
    """
    Configura o logger da aplicação.
    
    Args:
        filename: Nome do arquivo de log
        force_reconfigure: Se True, remove handlers existentes antes
    """
    logger = logging.getLogger()
    
    if force_reconfigure:
        # Remove handlers existentes
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    # Verifica se já existe handler para este arquivo
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            if handler.baseFilename == os.path.abspath(filename):
                return  # Já configurado
    
    # Adiciona novo handler
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

---

## 🟢 Bugs Baixa Prioridade

### Bug #5: Falta Validação de Path no SQLite

**Severidade:** 🟢 BAIXA  
**Arquivo:** `src/database/tipos_base/database.py`  
**Linha:** 22-39

**Descrição:**
A função `init_sqlite()` aceita qualquer string como path sem validação. Embora o risco seja baixo em uso normal, poderia ser explorado para:
- Tentar acessar arquivos do sistema
- Criar bancos em locais inesperados

**Código Problemático:**
```python
def init_sqlite(path: Optional[str] = None):
    if path is None:
        path = os.path.join(os.getcwd(), "database.db")
    
    # Nenhuma validação do path
    engine = create_engine(f"sqlite:///{path}", echo=SQL_ALCHEMY_DEBUG)
```

**Solução Recomendada:**
```python
def init_sqlite(path: Optional[str] = None):
    """Inicializa SQLite com validação de path."""
    if path is None:
        path = os.path.join(os.getcwd(), "database.db")
    
    # Validação básica
    path = os.path.abspath(path)
    
    # Verifica se não está tentando acessar fora do projeto
    project_root = os.path.abspath(os.getcwd())
    if not path.startswith(project_root) and not path.startswith('/tmp'):
        raise ValueError(f"Path não permitido: {path}")
    
    # Verifica se diretório existe ou pode ser criado
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    
    engine = create_engine(f"sqlite:///{path}", echo=SQL_ALCHEMY_DEBUG)
```

---

### Bug #6: Falta Validação de Tipos de Entrada

**Severidade:** 🟢 BAIXA  
**Arquivo:** Múltiplos arquivos

**Descrição:**
Muitas funções não validam os tipos de entrada, o que pode causar erros confusos ou comportamento inesperado quando valores incorretos são passados.

**Exemplos:**
```python
# Aceita None sem validar
Database.init_sqlite(None)  # Funciona, usa default

# Aceita tipos errados
Database.init_sqlite(123)  # TypeError só na conversão para string

# Aceita strings vazias
Database.init_sqlite("")  # Pode criar banco em lugar estranho
```

**Solução Recomendada:**
```python
from typing import Optional

def init_sqlite(path: Optional[str] = None):
    """Inicializa SQLite com validação de tipos."""
    # Validação de tipo
    if path is not None and not isinstance(path, str):
        raise TypeError(f"path deve ser string ou None, não {type(path)}")
    
    # Validação de valor
    if path is not None and not path.strip():
        raise ValueError("path não pode ser string vazia")
    
    # Resto da implementação...
```

---

## 📋 Checklist de Correções

### Prioridade Alta (Fazer Agora)
- [ ] **Bug #1:** Implementar shutdown gracioso da thread da API
- [ ] **Bug #2:** Adicionar lock e dispose no Database
- [ ] **Bug #3:** Criar função `parse_bool_env()` utilitária

### Prioridade Média (Fazer em Breve)
- [ ] **Bug #4:** Prevenir acúmulo de handlers de log
- [ ] Adicionar testes de integração para threads
- [ ] Implementar connection pooling adequado

### Prioridade Baixa (Melhorias)
- [ ] **Bug #5:** Validar paths do SQLite
- [ ] **Bug #6:** Adicionar validação de tipos em todas as funções públicas
- [ ] Adicionar type hints completos
- [ ] Configurar mypy para verificação de tipos

---

## 🧪 Cobertura de Testes

Os testes criados cobrem:
- ✅ Inicialização de banco de dados
- ✅ Gerenciamento de sessões
- ✅ Detecção de memory leaks
- ✅ Validação de entrada
- ✅ Segurança (SQL injection, path injection)
- ✅ Thread safety

**Para rodar todos os testes:**
```bash
pytest -v
```

**Para ver bugs documentados:**
```bash
pytest tests/memory/ -v
pytest tests/unit/test_validation_and_bugs.py -v
```

---

## 📞 Próximas Ações Recomendadas

1. **Corrigir Bug #1** - Crítico para produção
2. **Revisar código** em busca de outros usos de threads daemon
3. **Implementar CI/CD** para rodar testes automaticamente
4. **Configurar alerts** para memory leaks em produção
5. **Documentar** padrões de código para evitar novos bugs

---

**Nota:** Este relatório foi gerado durante a criação da suite de testes. Todos os bugs foram identificados através de análise estática e testes automatizados.
