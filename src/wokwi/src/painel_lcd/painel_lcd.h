#ifndef PAINEL_LCD_H
#define PAINEL_LCD_H

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include "../config.h"

class PainelLCD {
    uint8_t i2cAddr;
    uint8_t lcdCols;
    uint8_t lcdRows;
    uint8_t i2cSda;
    uint8_t i2cScl;
    LcdType lcdType;
    LiquidCrystal_I2C* lcd;
    bool lcdEnabled;

public:
        PainelLCD(uint8_t i2cAddr = LCD_I2C_ADDRESS, LcdType lcdType = SELECTED_LCD,
              uint8_t i2cSda = 21, uint8_t i2cScl = 22)
        : i2cAddr(i2cAddr), i2cSda(i2cSda), i2cScl(i2cScl), lcdType(lcdType),
          lcd(nullptr), lcdEnabled(false) {
        // Define cols and rows based on lcdType
        if (lcdType == LCD_16x2) {
            lcdCols = 16;
            lcdRows = 2;
        } else if (lcdType == LCD_20x4) {
            lcdCols = 20;
            lcdRows = 4;
        } else {
            // Default to 20x4 if unknown
            lcdCols = 20;
            lcdRows = 4;
        }
    }

    ~PainelLCD() {
        if (lcd != nullptr) {
            delete lcd;
        }
    }

    void setup();
    void clear();
    void printLCDSerial(uint8_t col, uint8_t row, const String& msg);
    void printFloatLcdSerial(uint8_t col, uint8_t row, const String& start, float value, const String& end = "");
    
    // Getters
    uint8_t getI2CAddr() const { return i2cAddr; }
    uint8_t getLcdCols() const { return lcdCols; }
    uint8_t getLcdRows() const { return lcdRows; }
    uint8_t getI2CSda() const { return i2cSda; }
    uint8_t getI2CScl() const { return i2cScl; }
    bool isEnabled() const { return lcdEnabled; }
};

#endif // PAINEL_LCD_H
