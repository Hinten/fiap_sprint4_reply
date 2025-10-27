# Plano de Ação (para um agente IA) — Correções e melhorias de testes

Objetivo
--------
Este documento descreve, de forma simples e executável, as correções e melhorias que devem ser aplicadas no repositório para reduzir skips, mitigar riscos (threads, vazamentos, estado global) e melhorar a robustez dos testes e do código. Cada item traz o arquivo a alterar, o objetivo, um esboço de mudança, como testar e o resultado esperado.

Pré-requisitos
--------------
- Ambiente Windows com `cmd.exe` ou terminal compatível.
- Python 3.11 e venv ativado (.venv). Exemplo:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Checklist (alta prioridade primeiro)
------------------------------------
1. Implementar shutdown gracioso da API (crítico)
2. Eliminar variáveis mutáveis de classe no Database (alto)
3. Evitar acumulo de handlers no logger (alto)
4. Padronizar parsing de booleanos de variáveis de ambiente (médio)
5. Adicionar fixtures para modelos Sensor/Leitura (médio)
6. Criar `requirements-dev.txt` e documentar testes opcionais (baixo)

Para cada tarefa a seguir há: arquivo(s) envolvidos, o que mudar, exemplo de código, comando(s) de teste e resultado esperado.

1) Shutdown gracioso da API (CRÍTICO)
------------------------------------
Arquivos alvo:
- `src/api/api_basica.py`

Objetivo:
- Evitar uso de thread daemon que pode ser finalizada abruptamente. Expor start/stop controlados e registrar shutdown em `atexit` e handlers de sinal.

O que fazer (passos):
- Substituir thread daemon por thread não-daemon ou, preferível, usar `uvicorn.Server` programaticamente.
- Expor funções: `start_api_background()`, `shutdown_api(timeout=5)` e registrar `atexit.register(shutdown_api)`.

Exemplo (esboço):
```python
# ...existing code...
import threading, atexit, signal
_shutdown_event = threading.Event()
_api_thread = None

def _run_api():
    # adaptar para iniciar uvicorn programaticamente ou chamar função iniciar_api mudando para controlar loop
    iniciar_api()

def start_api_background():
    global _api_thread
    if _api_thread and _api_thread.is_alive():
        return
    _api_thread = threading.Thread(target=_run_api, daemon=False)
    _api_thread.start()

def shutdown_api(timeout=5):
    _shutdown_event.set()
    if _api_thread:
        _api_thread.join(timeout=timeout)

atexit.register(shutdown_api)
# opcional: ligar signal handlers
signal.signal(signal.SIGINT, lambda *a: shutdown_api())
signal.signal(signal.SIGTERM, lambda *a: shutdown_api())
# ...existing code...
```

Testes a rodar:
```bat
tests\run_tests.bat integration
```
Resultado esperado:
- Testes de integração relacionados a threads não devem expor comportamentos de shutdown abrupto. Se houver testes específicos para daemon behaviour que antes estavam skipados, adaptar o teste para usar `start_api_background()` e `shutdown_api()`.

2) Refatorar `Database` para evitar variáveis de classe mutáveis (ALTO)
----------------------------------------------------------------------
Arquivos alvo:
- `src/database/tipos_base/database.py` (ou arquivo equivalente)

Objetivo:
- Garantir que `engine` e `session` não sejam variáveis de classe compartilhadas que causam race conditions.

O que fazer:
- Implementar `get_engine(url)` e `get_session()`; usar `scoped_session` ou factories e context managers.

Esboço:
```python
# ...existing code...
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

_engine = None
_SessionFactory = None

def init_db(url):
    global _engine, _SessionFactory
    if _engine is None:
        _engine = create_engine(url, pool_pre_ping=True)
        _SessionFactory = scoped_session(sessionmaker(bind=_engine))

def get_session():
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized")
    return _SessionFactory()

# Use with:
# with get_session() as session:
#     ...
```

Testes a rodar:
```bat
tests\run_tests.bat unit
```
Resultado esperado:
- Nenhum teste unitário de DB (ex.: TestDatabaseInitialization) deve falhar; resource leaks devem ser evitados.

3) Evitar acúmulo de handlers no `logger` (ALTO)
-----------------------------------------------
Arquivos alvo:
- `src/logger/config.py` (ou similar)

Problema:
- Cada chamada a `configurar_logger()` adiciona handlers adicionais.

Correção sugerida:
- Antes de adicionar handler novo, remover/fechar handlers existentes.

Exemplo:
```python
import logging

def configurar_logger(filename):
    logger = logging.getLogger()
    for h in logger.handlers[:]:
        try:
            logger.removeHandler(h)
            h.close()
        except Exception:
            pass
    handler = logging.FileHandler(filename)
    # configurar formatter
    logger.addHandler(handler)
```

Testes a rodar:
```bat
tests\run_tests.bat unit
```
Resultado esperado:
- `TestLoggingResourceLeaks::test_logger_handlers_cleanup` permanece verde e sem handlers duplicados.

4) Utilitário `parse_bool` para variáveis de ambiente (MÉDIO)
------------------------------------------------------------
Arquivos alvo:
- `src/dashboard/main.py`
- `src/api/api_basica.py`
- qualquer outro lugar que parseie variáveis booleanas do env

Problema:
- Parsing atual só aceita "true"; ignorando "1", "yes" etc.

Correção sugerida:
- Criar util em `src/utils/env_utils.py`:
```python
def parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ("true","1","yes","on")
```
- Substituir usos diretos por `parse_bool(os.environ.get(...))`.

Testes a rodar:
```bat
tests\run_tests.bat unit
```
Resultado esperado:
- `TestEnvironmentVariableHandling::test_bool_env_var_parsing` verde.

5) Fixtures para Sensor/Leitura (MÉDIO)
--------------------------------------
Arquivos alvo:
- `tests/conftest.py` (criar/atualizar)
- possivelmente `tests/integration/test_api.py` (usar fixtures)

Objetivo:
- Remover skips que dependem de configuração completa do modelo Sensor/Leitura criando fixtures que preparam DB/test doubles.

O que fazer:
- Adicionar fixtures:
  - `db_engine` ou `test_db` que cria uma base sqlite em memória e cria as tabelas necessárias antes do teste;
  - `sensor_factory` que insere um Sensor mínimo no DB e retorna o id;
  - `leitura_factory` para criar leituras.

Exemplo (pytest fixtures):
```python
import pytest
from src.database.tipos_base.database import init_db, get_session

@pytest.fixture(scope='session')
def test_db():
    init_db('sqlite:///:memory:')
    yield
    # cleanup se necessário

@pytest.fixture
def sensor_factory(test_db):
    session = get_session()
    sensor = Sensor(nome='s1')
    session.add(sensor)
    session.commit()
    yield sensor
    session.close()
```

Testes a rodar:
```bat
tests\run_tests.bat integration
```
Resultado esperado:
- `tests/integration/test_api.py::TestInitSensorEndpoint::test_init_sensor_post` deixa de ser skip e passa (ou é convertido para testar somente o endpoint em modo mock).

6) `requirements-dev.txt` e documentação (BAIXO)
-----------------------------------------------
Objetivo:
- Separar dependências pesadas (plotly, joblib, etc) para que desenvolvedores optem por instalar tudo quando precisarem rodar testes que dependem de dashboard/ML.

O que fazer:
- Criar `requirements-dev.txt` com libs extras (plotly, joblib, scikit-learn, etc).
- Atualizar `tests/README.md` com seção "Testes opcionais" e como instalar:
```bat
pip install -r requirements-dev.txt
```

Testes a rodar:
```bat
# se optar por instalar extras
pip install -r requirements-dev.txt
tests\run_tests.bat all
```
Resultado esperado:
- Menos skips (tests que exigem plotly/joblib passam quando as dependências extras forem instaladas).

Validação final e passos de commit
---------------------------------
Para cada alteração aplicada:
1. Rodar `pytest` (ou `tests\run_tests.bat <categoria>`) conforme indicado.
2. Verificar que os testes relacionados passam e que não há regressões.

Git / PR
--------
- Criar branch por tarefa, por exemplo:
  - `fix/api-shutdown` (shutdown API)
  - `fix/db-refactor` (DB)
  - `fix/logger-cleanup`
  - `feature/requirements-dev`
- Commits pequenos e descritivos:
  - `git checkout -b fix/api-shutdown`
  - `git add <files>`
  - `git commit -m "fix(api): implement graceful shutdown for API"`
  - `git push origin fix/api-shutdown`
- Abrir PR para cada branch com descrição do que foi alterado e comandos para validar localmente.

Estratégia de teste incremental (recomendada)
--------------------------------------------
- aplicar mudanças críticas primeiro (`api-shutdown`, `db-refactor`, `logger-cleanup`), testar, abrir PR;
- depois aplicar mudanças de médio porte (fixtures, parse_bool), testar e abrir PR;
- por fim, mexer em dev deps e documentação.

Caso algo falhe
---------------
- Reverter o commit localmente: `git reset --hard HEAD~1` (após confirmar o commit que causou problema)
- Rodar `pytest -k <nome_do_teste>` para isolar falha e debugar
- Logar a saída do pytest em arquivo com `pytest -q > run_tests_output.txt 2>&1` e anexar ao PR

Fim
---

Siga este passo a passo, aplicando uma mudança por vez e validando a suíte de testes antes de prosseguir para a próxima. Se quiser, eu mesmo aplico as mudanças (edito os arquivos e executo os testes) — diga qual item deseja que eu implemente primeiro e eu faço as alterações, executo os testes e envio o diff/PR preparado.

