# 🚀 Quick Start - Testes

Este guia rápido mostra como começar a rodar os testes em **menos de 2 minutos**.

## ⚡ Início Rápido (2 minutos)

### 1️⃣ Instalar Dependências (1 min)

```bash
# Criar ambiente virtual (opcional mas recomendado)
python -m venv .venv

# Ativar ambiente
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Rodar Testes (30 segundos)

```bash
# Opção mais simples
pytest

# Ou usar o helper script
./tests/run_tests.sh        # Linux/Mac
tests\run_tests.bat         # Windows
```

✅ **Pronto!** Você deve ver algo como:
```
===== 33 passed, 6 skipped in 3.41s =====
```

## 📋 Comandos Úteis

```bash
# Testes com output detalhado
pytest -v

# Apenas testes rápidos
./tests/run_tests.sh quick

# Com cobertura de código
./tests/run_tests.sh coverage

# Ver quais testes existem
./tests/run_tests.sh summary
```

## 📚 Documentação Completa

- **tests/TESTS.md** - Guia completo de testes
- **tests/BUG_REPORT.md** - Bugs encontrados e soluções
- **tests/README.md** - Estrutura dos testes

## 🐛 Bugs Importantes

### 🔴 CRÍTICO - Corrigir Primeiro
- **Thread daemon na API** (`src/api/api_basica.py:60`)
  - Causa: Thread finalizada abruptamente
  - Impacto: Conexões podem não fechar
  - Ver: tests/BUG_REPORT.md para solução

### 🟡 MÉDIO - Corrigir em Breve
- Estado global no Database
- Parsing de booleanos limitado
- Handlers de log acumulam

Veja **tests/BUG_REPORT.md** para detalhes completos.

## ❓ Problemas Comuns

### "ModuleNotFoundError: No module named 'pytest'"
```bash
pip install pytest pytest-cov pytest-mock
```

### Testes falhando
```bash
# Re-rodar apenas os que falharam
./tests/run_tests.sh failed
```

### Ver detalhes de falhas
```bash
pytest -vv --tb=long
```

## 🎯 Próximos Passos

1. ✅ Rode os testes: `./tests/run_tests.sh`
2. 📖 Leia: **tests/TESTS.md**
3. 🐛 Revise: **tests/BUG_REPORT.md**
4. 🔧 Corrija bugs críticos
5. 📈 Expanda cobertura de testes

## 💡 Dicas

- Use `./tests/run_tests.sh help` para ver todas as opções
- Execute `pytest -k "palavra"` para rodar testes específicos
- Use `pytest --lf` para re-rodar apenas testes que falharam
- Adicione `-vv` para output super detalhado

---

**Dúvidas?** Consulte tests/TESTS.md para documentação completa.

