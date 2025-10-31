# ESP32 Industrial Monitor - Modular Architecture

**Version 2.0** - Refactored with clean, modular design

## Overview

This is a complete refactoring of the ESP32 industrial monitoring system, porting modules from [fiap_fase5_cap1](https://github.com/Hinten/fiap_fase5_cap1) and implementing a clean, modular architecture with separated tasks for sensor reading and data transmission.

## Features

### Sensors
- **MPU6050**: 6-axis accelerometer/gyroscope with vibration detection
- **LDR**: Light sensor with lux calculation
- **Temperature**: Built-in MPU6050 temperature sensor

### Connectivity
- **WiFi**: Automatic connection and reconnection
- **HTTP API**: RESTful communication with backend
- **LCD Display**: Support for LCD_NONE, LCD_16x2, LCD_20x4

### Architecture
- **Primary Task**: Sensor readings every 5 seconds
- **Secondary Task**: Network operations (WiFi, API, data transmission)
- **Modular Design**: Separated concerns, reusable components
- **Clean Code**: Well-documented, easy to maintain

## Quick Start

### 1. Configuration
Edit `src/config.h`:
```cpp
// Choose LCD type
const LcdType SELECTED_LCD = LCD_16x2;  // or LCD_20x4 or LCD_NONE

// Network settings (auto-configured for Wokwi)
#define NETWORK_SSID "Wokwi-GUEST"
#define NETWORK_PASSWORD ""

// API endpoint
#define API_URL "http://localhost:8180"
```

### 2. Upload and Run
- **Wokwi**: Upload files and start simulation
- **PlatformIO**: `pio run --target upload`
- **Arduino IDE**: Open sketch.cpp and upload

### 3. Monitor
Open Serial Monitor (115200 baud) to see:
- Initialization messages
- Sensor readings
- Network status
- Data transmission

## Documentation

- **[REFACTORING.md](REFACTORING.md)** - Migration guide and changes
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Visual diagrams and structure
- **[COMPARISON.md](COMPARISON.md)** - Before/after code examples
- **[TESTING.md](TESTING.md)** - Complete testing guide

## Directory Structure

```
src/wokwi/
├── src/
│   ├── api/                    # HTTP API client
│   │   └── api.h
│   ├── conexao_wifi/           # WiFi connection
│   │   ├── conexao_wifi.h
│   │   └── conexao_wifi.cpp
│   ├── painel_lcd/             # LCD display
│   │   ├── painel_lcd.h
│   │   └── painel_lcd.cpp
│   ├── sensores/
│   │   ├── sensor_ldr/         # Light sensor
│   │   │   ├── sensor_ldr.h
│   │   │   └── sensor_ldr.cpp
│   │   └── mpu6050/            # Accelerometer/Gyro
│   │       ├── MPU6050Sensor.h
│   │       └── MPU6050Sensor.cpp
│   ├── config.h                # Configuration
│   ├── sketch.cpp              # Main application
│   └── sketch_original.cpp     # Original (backup)
├── platformio.ini              # PlatformIO config
├── diagram.json                # Wokwi circuit
├── libraries.txt               # Wokwi libraries
├── validate_structure.sh       # Validation script
└── *.md                        # Documentation
```

## Module Overview

### API Module (`api/`)
HTTP client for backend communication
- GET/POST methods
- Automatic chip ID injection
- JSON response parsing
- 120 lines

### ConexaoWifi Module (`conexao_wifi/`)
WiFi connection management
- Automatic connection with timeout
- Status checking
- Reconnection support
- 80 lines

### PainelLCD Module (`painel_lcd/`)
LCD display abstraction
- Support for 3 LCD types (NONE, 16x2, 20x4)
- Automatic line clearing
- Serial mirroring
- 150 lines

### SensorLDR Module (`sensores/sensor_ldr/`)
Light sensor driver
- Raw ADC reading
- Lux calculation
- Calibration support
- 50 lines

### MPU6050Sensor Module (`sensores/mpu6050/`)
Accelerometer/Gyroscope driver
- Initialization and testing
- Acceleration/gyro/temperature reading
- Vibration calculation
- Calibration support
- 160 lines

## Task Architecture

### Primary Task (Sensor Reading)
Executes every 5 seconds:
1. Read all sensors (MPU6050, LDR)
2. Calculate vibration
3. Update LCD display
4. Check alert thresholds
5. Trigger buzzer/LED if needed

### Secondary Task (Network Operations)
Executes continuously (100ms delay):
1. Check WiFi connection
2. Initialize sensor with API
3. Prepare JSON data
4. Send to backend API
5. Handle responses

### Main Loop
Simple timing logic that delegates to tasks:
```cpp
void loop() {
    if (time_for_primary_task) {
        primaryTask();
    } else {
        secondaryTask();
    }
}
```

## Hardware Requirements

### ESP32 Board
- ESP32 Dev Module (or compatible)
- USB cable for programming

### Sensors
- MPU6050 (I2C accelerometer/gyroscope)
- LDR (photoresistor) with 10kΩ resistor
- LCD 16x2 or 20x4 with I2C adapter (optional)

### Actuators
- LED (pin 15)
- Buzzer (pin 2)
- Relay (pin 32) - optional

### Connections
```
MPU6050:  SDA → GPIO 21, SCL → GPIO 22
LCD:      SDA → GPIO 21, SCL → GPIO 22
LDR:      Signal → GPIO 34
LED:      GPIO 15
Buzzer:   GPIO 2
Relay:    GPIO 32
```

## Libraries Required

- **ArduinoJson** (7.4.1+)
- **MPU6050** by Electronic Cats (1.4.3+)
- **LiquidCrystal_I2C** (1.1.4+)

Install via PlatformIO or Arduino Library Manager.

## Configuration Options

### LCD Type Selection
```cpp
const LcdType SELECTED_LCD = LCD_16x2;  // LCD_NONE, LCD_16x2, LCD_20x4
```

### Timing
```cpp
const unsigned long PRIMARY_TASK_INTERVAL = 5000;   // 5 seconds
const unsigned long SECONDARY_TASK_DELAY = 100;     // 100ms
```

### Thresholds
```cpp
const float VIBRATION_THRESHOLD = 1.0;
const int VIBRATION_SAMPLES = 100;
```

### Pins
All pin definitions in `config.h`

## Validation

Run the validation script:
```bash
./validate_structure.sh
```

Expected output:
```
✓ All directories present
✓ All header files present
✓ All implementation files present
✓ No circular dependencies
✓ All header guards in place
```

## Testing

See [TESTING.md](TESTING.md) for comprehensive testing guide.

Quick test:
1. Upload to ESP32 or Wokwi
2. Open Serial Monitor (115200 baud)
3. Verify initialization
4. Watch sensor readings
5. Check LCD display (if connected)

## Performance

- Boot time: ~2-3 seconds
- Primary task: ~500ms
- Secondary task: ~100ms cycle
- Memory usage: ~50-60KB
- WiFi connection: ~5-10 seconds

## Troubleshooting

### "MPU6050 connection failed"
- Check I2C wiring (SDA=21, SCL=22)
- Verify MPU6050 address (0x68 or 0x69)

### "WiFi desconectado"
- Check SSID/password in config.h
- Ensure WiFi network is available

### "LCD not displaying"
- Verify LCD type in config.h
- Check I2C address (default 0x27)
- Check wiring

### Compilation errors
- Install all required libraries
- Check file structure with validate_structure.sh

## Migration from v1.0

The original monolithic code is preserved in `src/sketch_original.cpp`.

Key changes:
- WiFi connection → `ConexaoWifi` class
- API communication → `Api` class
- MPU6050 code → `MPU6050Sensor` class
- LDR reading → `SensorLDR` class
- LCD output → `PainelLCD` class
- Tasks separated: reading vs transmission

See [COMPARISON.md](COMPARISON.md) for detailed before/after examples.

## Benefits of Refactoring

1. **Modularity**: Each component is self-contained
2. **Reusability**: Modules work in other projects
3. **Testability**: Test modules independently
4. **Maintainability**: Easy to update/fix
5. **Readability**: Clear code organization
6. **Scalability**: Simple to add features
7. **Documentation**: Self-documenting modules

## Future Enhancements

- [ ] FreeRTOS tasks for true multitasking
- [ ] Queue-based inter-task communication
- [ ] MQTT support
- [ ] OTA updates
- [ ] Web configuration portal
- [ ] SD card logging
- [ ] Power management

## Credits

- Original project: [fiap_sprint4_reply](https://github.com/Hinten/fiap_sprint4_reply)
- Modules ported from: [fiap_fase5_cap1](https://github.com/Hinten/fiap_fase5_cap1)
- Architecture inspired by: Clean Architecture principles

## License

Same as the original project.

## Support

For issues or questions:
1. Check documentation (*.md files)
2. Run validation script
3. Compare with original code
4. Review architecture diagrams

---

**Version 2.0** - Modular Architecture | Refactored 2025
