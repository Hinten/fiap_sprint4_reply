#include "painel_lcd.h"
#include <Wire.h>

void PainelLCD::setup() {
    // Initialize I2C
    Wire.begin(i2cSda, i2cScl);
    
    // Configure LCD based on selected type
    if (lcdType == LCD_NONE) {
        lcdEnabled = false;
        Serial.println(F("LCD Mode: NONE (Serial only)"));
        return;
    }
    
    // Determine LCD dimensions based on type
    if (lcdType == LCD_16x2) {
        lcdCols = 16;
        lcdRows = 2;
        Serial.println(F("LCD Mode: 16x2"));
    } else if (lcdType == LCD_20x4) {
        lcdCols = 20;
        lcdRows = 4;
        Serial.println(F("LCD Mode: 20x4"));
    }
    
    // Initialize LCD
    lcd = new LiquidCrystal_I2C(i2cAddr, lcdCols, lcdRows);
    lcd->init();
    lcd->backlight();
    lcd->clear();
    lcdEnabled = true;
    
    // Display initialization message
    lcd->setCursor(0, 0);
    lcd->print(F("Iniciando..."));
    Serial.println(F("LCD initialized successfully"));
    
    delay(1000);
    lcd->clear();
}

void PainelLCD::clear() {
    if (lcdEnabled && lcd != nullptr) {
        lcd->clear();
    }
    Serial.println(F("--- LCD Cleared ---"));
}

void PainelLCD::printLCDSerial(uint8_t col, uint8_t row, const String& msg) {
    // Always print to Serial
    Serial.print(F("[LCD "));
    Serial.print(col);
    Serial.print(F(","));
    Serial.print(row);
    Serial.print(F("] "));
    Serial.println(msg);
    
    // If LCD disabled, return
    if (!lcdEnabled || lcd == nullptr) {
        return;
    }
    
    // Check if row is out of bounds
    if (row >= lcdRows) {
        row = row % lcdRows;
    }
    
    // Set cursor and clear the line
    lcd->setCursor(0, row);
    for (uint8_t i = 0; i < lcdCols; i++) {
        lcd->print(' ');
    }
    
    // Print message
    lcd->setCursor(col, row);
    
    // Truncate if necessary
    size_t maxLen = lcdCols - col;
    if (msg.length() > maxLen) {
        String truncated = msg.substring(0, maxLen);
        lcd->print(truncated);
    } else {
        lcd->print(msg);
    }
}

void PainelLCD::printFloatLcdSerial(uint8_t col, uint8_t row, const String& start, float value, const String& end) {
    if (isnan(value)) {
        printLCDSerial(col, row, start + " Error");
    } else {
        printLCDSerial(col, row, start + String(value) + end);
    }
}
