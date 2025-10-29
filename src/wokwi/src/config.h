#ifndef CONFIG_H
#define CONFIG_H

/**
 * Configuração do tipo de painel LCD
 * 
 * Escolha uma das opções abaixo:
 * - LCD_NONE: Nenhum LCD conectado (apenas saída Serial)
 * - LCD_16x2: Painel LCD 16 colunas x 2 linhas
 * - LCD_20x4: Painel LCD 20 colunas x 4 linhas (padrão)
 */
enum LcdType {
  LCD_NONE = 0,
  LCD_16x2 = 1,
  LCD_20x4 = 2
};

// ===== CONFIGURAÇÃO DO USUÁRIO =====
// Altere esta linha para escolher o tipo de LCD:
const LcdType SELECTED_LCD = LCD_20x4;

// Configurações do LCD I2C
const int LCD_I2C_ADDRESS = 0x27;

// Delay para paginação de conteúdo (quando necessário para LCD 16x2)
const int DISPLAY_PAGE_DELAY_MS = 2000;

#endif // CONFIG_H
