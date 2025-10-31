# ESP32 Sensor Monitoring System - Wokwi Simulation

## 🎯 Overview

This directory contains the Arduino/ESP32 firmware for the industrial equipment monitoring system. The code reads sensors (MPU6050 accelerometer/gyroscope, LDR photoresistor) and sends data to the backend API.

## 🆕 Recent Refactoring (October 2025)

The display system was completely refactored to support multiple LCD configurations. See [REFATORACAO.md](REFATORACAO.md) for complete details.

### Quick Summary
- ✅ Support for LCD 20x4, 16x2, or no LCD (Serial only)
- ✅ Centralized display management
- ✅ Automatic pagination for smaller displays
- ✅ Fixed 7 critical bugs
- ✅ Improved memory management

## 📁 File Structure

```
src/wokwi/
├── src/
│   ├── sketch.cpp              # Main Arduino sketch (refactored)
│   ├── config.h                # LCD type configuration ⭐ NEW
│   ├── display_manager.h       # Display function declarations ⭐ NEW
│   └── display_manager.cpp     # Display implementation ⭐ NEW
├── platformio.ini              # PlatformIO configuration
├── diagram.json                # Wokwi circuit diagram
├── libraries.txt               # Wokwi library dependencies
├── REFATORACAO.md              # Complete refactoring documentation ⭐ NEW
├── VALIDACAO.md                # Testing and validation guide ⭐ NEW
└── README.md                   # This file ⭐ NEW
```

## 🚀 Quick Start

### 1. Choose LCD Type

Edit `src/config.h`:

```cpp
const LcdType SELECTED_LCD = LCD_20x4;  // Options: LCD_20x4, LCD_16x2, LCD_NONE
```

### 2. Compile and Upload

```bash
# Using PlatformIO
cd src/wokwi
pio run --target upload

# Or using Arduino IDE
# Open sketch.cpp and upload normally
```

### 3. Monitor Output

```bash
pio device monitor
# Or use Arduino IDE Serial Monitor at 115200 baud
```

## 🔧 Configuration Options

### LCD Types

| Type | Description | Rows | Cols |
|------|-------------|------|------|
| `LCD_20x4` | Standard 20x4 LCD (default) | 4 | 20 |
| `LCD_16x2` | Compact 16x2 LCD | 2 | 16 |
| `LCD_NONE` | No LCD (Serial Monitor only) | - | - |

### Other Settings in `config.h`

```cpp
const int LCD_I2C_ADDRESS = 0x27;         // I2C address of LCD
const int DISPLAY_PAGE_DELAY_MS = 2000;   // Delay between pages (16x2 mode)
```

## 📊 Display Functions

The new display manager provides these functions:

| Function | Purpose | Example |
|----------|---------|---------|
| `displayInit()` | Initialize display | Called in `setup()` |
| `displayPrint(msg)` | Print simple message | `displayPrint("Hello")` |
| `displayPrintAt(col, row, msg)` | Print at position | `displayPrintAt(0, 1, "Line 2")` |
| `displayPrintf(col, row, fmt, ...)` | Print with formatting | `displayPrintf(0, 0, "Temp: %.1f", temp)` |
| `displayClear()` | Clear display | `displayClear()` |

## 🐛 Bugs Fixed

1. **Hardcoded LCD size** - Now configurable
2. **String memory leaks** - Replaced with snprintf()
3. **Unsynchronized LCD/Serial** - Now automatic
4. **Row overflow on 16x2** - Auto-pagination added
5. **RAM waste** - F() macro for string literals
6. **Non-reusable initialization** - Now modular
7. **Incorrect comments** - Fixed technical accuracy

See [REFATORACAO.md](REFATORACAO.md) for complete bug details.

## 🧪 Testing

### Hardware Requirements
- ESP32 DevKit C v4
- MPU6050 (I2C address 0x68)
- LCD 20x4 or 16x2 with I2C backpack (address 0x27)
- LDR (photoresistor) on pin 34
- LED on pin 15
- Buzzer on pin 2
- Relay module on pin 32

### Testing Checklist

- [ ] Compile without errors
- [ ] Upload to ESP32
- [ ] LCD initializes correctly
- [ ] WiFi connects
- [ ] Sensor readings display
- [ ] API communication works
- [ ] Alerts trigger properly
- [ ] Serial Monitor shows all data

### Testing Different LCD Modes

```bash
# Test 20x4 (default)
# config.h: SELECTED_LCD = LCD_20x4
pio run --target upload

# Test 16x2 (with pagination)
# config.h: SELECTED_LCD = LCD_16x2
pio run --target upload

# Test Serial only
# config.h: SELECTED_LCD = LCD_NONE
pio run --target upload
```

## 🌐 Wokwi Simulation

This project can be simulated on Wokwi:
1. Go to [wokwi.com](https://wokwi.com)
2. Upload `diagram.json` and `src/sketch.cpp`
3. Add libraries from `libraries.txt`
4. Run simulation

**Note:** The simulation uses LCD 20x4 by default (as defined in `diagram.json`).

## 📡 API Integration

The ESP32 sends sensor data to the backend API defined in environment variables:

```cpp
const char* ssid = NETWORK_SSID;          // From platformio.ini
const char* password = NETWORK_PASSWORD;   // From platformio.ini
const char* endpoint_api = API_URL;        // From .env file
```

### API Endpoints

- `POST /init/` - Register sensor with chip ID
- `POST /leitura/` - Send sensor readings

### Data Format

```json
{
  "serial": "0123456789ABCDEF",
  "temperatura": 25.5,
  "lux": 1200,
  "vibracao_media": 0.45,
  "acelerometro_x": 0.02,
  "acelerometro_y": -0.01,
  "acelerometro_z": 0.98
}
```

## 🔒 Security Notes

- ✅ No hardcoded credentials in source code
- ✅ Buffer overflow protection with snprintf()
- ✅ Null pointer checks before LCD operations
- ✅ Static memory allocation (no dynamic allocation)
- ⚠️ WiFi credentials should be in environment variables

## 📚 Documentation

- **[REFATORACAO.md](REFATORACAO.md)** - Complete refactoring documentation (Portuguese)
  - What was changed
  - How to use (ELI5)
  - Technical details
  - Bugs fixed with explanations
  
- **[VALIDACAO.md](VALIDACAO.md)** - Testing and validation guide (Portuguese)
  - Test procedures
  - Code metrics
  - Safety checks
  - Future improvements

## 🛠️ Development

### Adding New Display Messages

```cpp
// Option 1: Simple message
displayPrint("New message");

// Option 2: Positioned message
displayPrintAt(0, 1, "Line 2 text");

// Option 3: Formatted message
displayPrintf(0, 0, "Value: %.2f", myVariable);
```

**Important:** Never use `lcd.print()` or direct Serial.print() for display text. Always use the display manager functions.

### Changing LCD Configuration

1. Edit `src/config.h`
2. Change `SELECTED_LCD` value
3. Recompile and upload
4. No code changes needed!

### Memory Optimization Tips

- Use `F()` macro for string literals: `Serial.println(F("text"));`
- Avoid `String()` class, use `char[]` arrays instead
- Use `snprintf()` for string formatting
- Keep buffers on stack, not heap

## 🤝 Contributing

When modifying the display code:

1. ✅ DO use display manager functions
2. ✅ DO use F() macro for literals
3. ✅ DO use snprintf() for formatting
4. ✅ DO test with all 3 LCD modes
5. ❌ DON'T use lcd.print() directly
6. ❌ DON'T use String() concatenation
7. ❌ DON'T assume specific LCD size

## 📞 Support

For issues related to:
- **Display system**: See [REFATORACAO.md](REFATORACAO.md)
- **Testing**: See [VALIDACAO.md](VALIDACAO.md)
- **General project**: See root [README.md](../../README.md)

## 📄 License

This project is part of FIAP Sprint 4. See root directory for license information.

---

**Last Updated:** October 2025  
**Version:** 2.0 (Refactored Display System)
