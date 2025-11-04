#include "display_manager.h"
#include <LiquidCrystal_I2C.h>
#include <stdarg.h>

// Instância global do LCD
static LiquidCrystal_I2C* lcd = nullptr;

// Configurações do display atual
static uint8_t lcdCols = 20;
static uint8_t lcdRows = 4;
static bool lcdEnabled = false;

// Buffer para formatação de strings
static char displayBuffer[128];

void displayInit() {
  // Inicializa Serial Monitor
  Serial.begin(115200);
  delay(100);
  Serial.println(F("=== Display Manager Initialized ==="));
  
  // Configura LCD baseado na seleção do usuário
  if (SELECTED_LCD == LCD_NONE) {
    lcdEnabled = false;
    Serial.println(F("LCD Mode: NONE (Serial only)"));
    return;
  }
  
  // Determina dimensões do LCD
  if (SELECTED_LCD == LCD_16x2) {
    lcdCols = 16;
    lcdRows = 2;
    Serial.println(F("LCD Mode: 16x2"));
  } else if (SELECTED_LCD == LCD_20x4) {
    lcdCols = 20;
    lcdRows = 4;
    Serial.println(F("LCD Mode: 20x4"));
  }
  
  // Inicializa o LCD
  lcd = new LiquidCrystal_I2C(LCD_I2C_ADDRESS, lcdCols, lcdRows);
  lcd->init();
  lcd->backlight();
  lcd->clear();
  lcdEnabled = true;
  
  // Mensagem de confirmação
  if (lcdEnabled) {
    lcd->setCursor(0, 0);
    lcd->print(F("LCD OK!"));
    Serial.println(F("LCD initialized successfully"));
  }
}

void displayClear() {
  if (lcdEnabled && lcd != nullptr) {
    lcd->clear();
  }
  Serial.println(F("--- LCD Cleared ---"));
}

void displayPrint(const char* message) {
  // Sempre imprime no Serial
  Serial.println(message);
  
  // Se LCD desabilitado, retorna
  if (!lcdEnabled || lcd == nullptr) {
    return;
  }
  
  // Imprime no LCD
  lcd->clear();
  lcd->setCursor(0, 0);
  
  // Trunca se necessário
  size_t len = strlen(message);
  if (len > lcdCols) {
    // Para mensagens longas, divide em linhas
    uint8_t row = 0;
    size_t pos = 0;
    
    while (pos < len && row < lcdRows) {
      lcd->setCursor(0, row);
      
      // Calcula quanto pode caber nesta linha
      size_t chunk = min((size_t)lcdCols, len - pos);
      
      // Copia para buffer temporário
      char lineBuffer[21]; // Máximo 20 chars + null terminator
      strncpy(lineBuffer, message + pos, chunk);
      lineBuffer[chunk] = '\0';
      
      lcd->print(lineBuffer);
      
      pos += chunk;
      row++;
    }
  } else {
    lcd->print(message);
  }
}

void displayPrintAt(uint8_t col, uint8_t row, const char* message) {
  // Sempre imprime no Serial com indicação de posição
  snprintf(displayBuffer, sizeof(displayBuffer), "[%d,%d] %s", col, row, message);
  Serial.println(displayBuffer);
  
  // Se LCD desabilitado, retorna
  if (!lcdEnabled || lcd == nullptr) {
    return;
  }
  
  // Verifica se a linha está fora do alcance do display atual
  if (row >= lcdRows) {
    // Para LCD 16x2, se tentar escrever na linha 2 ou 3, usa paginação
    if (SELECTED_LCD == LCD_16x2 && row >= 2) {
      // Limpa, aguarda e mostra na primeira linha
      lcd->clear();
      delay(DISPLAY_PAGE_DELAY_MS);
      row = (row - 2) % 2; // Mapeia linha 2->0, 3->1
    } else {
      // Para outros casos, simplesmente ignora ou mapeia para última linha
      row = lcdRows - 1;
    }
  }
  
  // Garante que col está dentro do limite
  if (col >= lcdCols) {
    col = 0;
  }
  
  lcd->setCursor(col, row);
  
  // Trunca a mensagem se ultrapassar o limite de colunas
  size_t maxLen = lcdCols - col;
  size_t msgLen = strlen(message);
  
  if (msgLen > maxLen) {
    char lineBuffer[21];
    strncpy(lineBuffer, message, maxLen);
    lineBuffer[maxLen] = '\0';
    lcd->print(lineBuffer);
  } else {
    lcd->print(message);
  }
}

void displayPrintLines(const char* lines[], uint8_t lineCount) {
  // Sempre imprime todas as linhas no Serial
  Serial.println(F("--- Multiple Lines ---"));
  for (uint8_t i = 0; i < lineCount; i++) {
    snprintf(displayBuffer, sizeof(displayBuffer), "Line %d: %s", i, lines[i]);
    Serial.println(displayBuffer);
  }
  Serial.println(F("--- End Lines ---"));
  
  // Se LCD desabilitado, retorna
  if (!lcdEnabled || lcd == nullptr) {
    return;
  }
  
  // Implementa paginação para displays com menos linhas
  uint8_t currentLine = 0;
  uint8_t page = 0;
  
  while (currentLine < lineCount) {
    if (page > 0) {
      // Aguarda antes de mostrar próxima página
      delay(DISPLAY_PAGE_DELAY_MS);
    }
    
    lcd->clear();
    
    // Imprime até lcdRows linhas ou até acabar as linhas
    for (uint8_t row = 0; row < lcdRows && currentLine < lineCount; row++, currentLine++) {
      lcd->setCursor(0, row);
      
      // Trunca se necessário
      size_t len = strlen(lines[currentLine]);
      if (len > lcdCols) {
        char lineBuffer[21];
        strncpy(lineBuffer, lines[currentLine], lcdCols);
        lineBuffer[lcdCols] = '\0';
        lcd->print(lineBuffer);
      } else {
        lcd->print(lines[currentLine]);
      }
    }
    
    page++;
  }
}

void displayPrintf(uint8_t col, uint8_t row, const char* format, ...) {
  va_list args;
  va_start(args, format);
  vsnprintf(displayBuffer, sizeof(displayBuffer), format, args);
  va_end(args);
  
  displayPrintAt(col, row, displayBuffer);
}

void displayPrintf(const char* format, ...) {
  va_list args;
  va_start(args, format);
  vsnprintf(displayBuffer, sizeof(displayBuffer), format, args);
  va_end(args);
  
  displayPrint(displayBuffer);
}
