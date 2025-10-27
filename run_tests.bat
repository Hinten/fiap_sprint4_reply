@echo off
REM Script para rodar diferentes cenários de testes no Windows
REM Uso: run_tests.bat [opção]

setlocal enabledelayedexpansion

echo ======================================
echo   FIAP Sprint 4 - Test Runner
echo ======================================
echo.

set TEST_TYPE=%1
if "%TEST_TYPE%"=="" set TEST_TYPE=all

if "%TEST_TYPE%"=="unit" goto unit
if "%TEST_TYPE%"=="integration" goto integration
if "%TEST_TYPE%"=="memory" goto memory
if "%TEST_TYPE%"=="coverage" goto coverage
if "%TEST_TYPE%"=="quick" goto quick
if "%TEST_TYPE%"=="failed" goto failed
if "%TEST_TYPE%"=="verbose" goto verbose
if "%TEST_TYPE%"=="all" goto all
if "%TEST_TYPE%"=="summary" goto summary
if "%TEST_TYPE%"=="help" goto help
if "%TEST_TYPE%"=="-h" goto help
if "%TEST_TYPE%"=="--help" goto help

echo Opção inválida: %TEST_TYPE%
echo Use 'run_tests.bat help' para ver opções disponíveis
exit /b 1

:unit
echo Rodando apenas testes unitários...
echo.
python -m pytest tests/unit/ -v
goto end

:integration
echo Rodando testes de integração...
echo.
python -m pytest tests/integration/ -v
goto end

:memory
echo Rodando testes de memória...
echo.
python -m pytest tests/memory/ -v
goto end

:coverage
echo Rodando testes com cobertura de código...
echo.
python -m pytest --cov=src --cov-report=html --cov-report=term
echo.
echo Relatório HTML gerado em: htmlcov\index.html
goto end

:quick
echo Rodando testes rápidos (sem slow)...
echo.
python -m pytest -m "not slow" -v
goto end

:failed
echo Re-rodando apenas testes que falharam anteriormente...
echo.
python -m pytest --lf -v
goto end

:verbose
echo Rodando todos os testes (modo verbose)...
echo.
python -m pytest -vv --tb=long
goto end

:all
echo Rodando todos os testes...
echo.
python -m pytest -v
goto end

:summary
echo Sumário dos testes...
echo.
python -m pytest --collect-only -q
echo.
echo Use 'run_tests.bat [opção]' para rodar testes específicos
goto end

:help
echo Uso: run_tests.bat [opção]
echo.
echo Opções disponíveis:
echo   all         - Roda todos os testes (padrão)
echo   unit        - Apenas testes unitários
echo   integration - Apenas testes de integração
echo   memory      - Apenas testes de memory leak
echo   coverage    - Testes com relatório de cobertura
echo   quick       - Testes rápidos (pula testes marcados como slow)
echo   failed      - Re-roda apenas testes que falharam
echo   verbose     - Todos os testes com output detalhado
echo   summary     - Mostra sumário dos testes disponíveis
echo   help        - Mostra esta mensagem
echo.
echo Exemplos:
echo   run_tests.bat unit
echo   run_tests.bat coverage
echo   run_tests.bat quick
goto end

:end
echo.
echo ======================================
echo Concluído!
echo ======================================
