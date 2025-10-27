#!/bin/bash
# Script para rodar diferentes cenários de testes
# Uso: ./tests/run_tests.sh [opção]

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  FIAP Sprint 4 - Test Runner${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Função para rodar testes
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "${YELLOW}▶ Executando: ${test_name}${NC}"
    echo -e "${BLUE}Comando: ${test_command}${NC}"
    echo ""

    if eval "$test_command"; then
        echo -e "${GREEN}✓ ${test_name} - SUCESSO${NC}"
    else
        echo -e "${RED}✗ ${test_name} - FALHOU${NC}"
        return 1
    fi
    echo ""
}

# Opções do script
case "${1:-all}" in
    "unit")
        echo -e "${BLUE}Rodando apenas testes unitários...${NC}\n"
        run_test "Testes Unitários" "python -m pytest tests/unit/ -v"
        ;;

    "integration")
        echo -e "${BLUE}Rodando testes de integração...${NC}\n"
        run_test "Testes de Integração" "python -m pytest tests/integration/ -v"
        ;;

    "memory")
        echo -e "${BLUE}Rodando testes de memória...${NC}\n"
        run_test "Testes de Memory Leak" "python -m pytest tests/memory/ -v"
        ;;

    "coverage")
        echo -e "${BLUE}Rodando testes com cobertura de código...${NC}\n"
        run_test "Cobertura de Código" "python -m pytest --cov=src --cov-report=html --cov-report=term"
        echo -e "${GREEN}Relatório HTML gerado em: htmlcov/index.html${NC}"
        ;;

    "quick")
        echo -e "${BLUE}Rodando testes rápidos (sem slow)...${NC}\n"
        run_test "Testes Rápidos" "python -m pytest -m 'not slow' -v"
        ;;

    "failed")
        echo -e "${BLUE}Re-rodando apenas testes que falharam anteriormente...${NC}\n"
        run_test "Testes Falhados" "python -m pytest --lf -v"
        ;;

    "verbose")
        echo -e "${BLUE}Rodando todos os testes (modo verbose)...${NC}\n"
        run_test "Todos os Testes (Verbose)" "python -m pytest -vv --tb=long"
        ;;

    "all")
        echo -e "${BLUE}Rodando todos os testes...${NC}\n"
        run_test "Todos os Testes" "python -m pytest -v"
        ;;

    "summary")
        echo -e "${BLUE}Sumário dos testes...${NC}\n"
        python -m pytest --collect-only -q
        echo ""
        echo -e "${GREEN}Use './tests/run_tests.sh [opção]' para rodar testes específicos${NC}"
        ;;

    "help"|"-h"|"--help")
        echo "Uso: ./tests/run_tests.sh [opção]"
        echo ""
        echo "Opções disponíveis:"
        echo "  all         - Roda todos os testes (padrão)"
        echo "  unit        - Apenas testes unitários"
        echo "  integration - Apenas testes de integração"
        echo "  memory      - Apenas testes de memory leak"
        echo "  coverage    - Testes com relatório de cobertura"
        echo "  quick       - Testes rápidos (pula testes marcados como slow)"
        echo "  failed      - Re-roda apenas testes que falharam"
        echo "  verbose     - Todos os testes com output detalhado"
        echo "  summary     - Mostra sumário dos testes disponíveis"
        echo "  help        - Mostra esta mensagem"
        echo ""
        echo "Exemplos:"
        echo "  ./tests/run_tests.sh unit"
        echo "  ./tests/run_tests.sh coverage"
        echo "  ./tests/run_tests.sh quick"
        ;;

    *)
        echo -e "${RED}Opção inválida: $1${NC}"
        echo "Use './tests/run_tests.sh help' para ver opções disponíveis"
        exit 1
        ;;
esac

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✓ Concluído!${NC}"
echo -e "${BLUE}======================================${NC}"

