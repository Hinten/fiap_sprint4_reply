#ifndef DISPLAY_MANAGER_H
#define DISPLAY_MANAGER_H

#include <Arduino.h>
#include "config.h"

/**
 * Display Manager - Gerenciador centralizado de exibição
 * 
 * Todas as funções de saída (LCD e Serial) passam por este módulo.
 * Garante que tudo exibido no LCD também seja enviado ao Serial Monitor.
 */

/**
 * Inicializa o display (LCD e Serial)
 * Deve ser chamado no setup()
 */
void displayInit();

/**
 * Limpa o display LCD
 * Também envia uma marcação ao Serial
 */
void displayClear();

/**
 * Imprime uma mensagem no LCD e no Serial
 * Centraliza a linha na primeira linha do LCD (ou divide em múltiplas se necessário)
 * 
 * @param message Mensagem a ser exibida
 */
void displayPrint(const char* message);

/**
 * Imprime uma mensagem em uma posição específica do LCD e no Serial
 * Adaptação automática para diferentes tamanhos de LCD
 * 
 * @param col Coluna (0-indexed)
 * @param row Linha (0-indexed)
 * @param message Mensagem a ser exibida
 */
void displayPrintAt(uint8_t col, uint8_t row, const char* message);

/**
 * Imprime múltiplas linhas no LCD com paginação automática
 * Ideal para exibir várias informações de uma vez
 * 
 * @param lines Array de strings com as linhas
 * @param lineCount Número de linhas no array
 */
void displayPrintLines(const char* lines[], uint8_t lineCount);

/**
 * Imprime com formatação (similar a printf)
 * 
 * @param col Coluna inicial
 * @param row Linha inicial
 * @param format String de formato (estilo printf)
 * @param ... Argumentos variáveis
 */
void displayPrintf(uint8_t col, uint8_t row, const char* format, ...);

/**
 * Versão sem posicionamento da displayPrintf
 * Imprime na linha atual do LCD
 */
void displayPrintf(const char* format, ...);

#endif // DISPLAY_MANAGER_H
