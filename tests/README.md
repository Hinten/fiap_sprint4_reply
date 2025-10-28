# 🧪 Tests - Suíte de Testes

## 📁 Estrutura

```
tests/
├── __init__.py              # Inicialização do pacote
├── conftest.py              # Configurações e fixtures do pytest
├── unit/                    # Testes unitários
│   ├── test_database.py     # Testes do módulo Database
│   └── test_validation_and_bugs.py  # Testes de validação e bugs
├── integration/             # Testes de integração
│   └── test_api.py          # Testes da API FastAPI
└── memory/                  # Testes de vazamento de memória
    └── test_memory_leaks.py # Detecção de memory leaks
```

## 🚀 Execução Rápida

```bash
# Todos os testes
pytest

# Apenas testes que passam
pytest -v

# Com cobertura
pytest --cov=src --cov-report=html
```

## 📊 Estatísticas Atuais

- ✅ **33 testes passando**
- ⏭️ **6 testes pulados** (requerem dependências opcionais)
- 🔍 **3 categorias de testes**
- 🐛 **6 bugs documentados**

## 📚 Documentação Completa

Veja [TESTS.md](TESTS.md) na pasta `tests/` para documentação detalhada.
