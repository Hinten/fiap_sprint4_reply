# ESP32 Refactoring - Modular Architecture

## Overview
This refactoring ports modules from the fiap_fase5_cap1 project and reorganizes the ESP32 code into a clean, modular architecture with separate tasks for sensor reading and data transmission.

## Changes Made

### 1. Ported Modules

#### API Module (`api/api.h`)
- **Purpose**: Handles HTTP communication with the backend API
- **Features**:
  - GET and POST methods
  - Automatic chip ID generation
  - Response struct with JSON parsing
  - Methods: `post_init()`, `post_leitura()`

#### ConexaoWifi Module (`conexao_wifi/`)
- **Files**: `conexao_wifi.h`, `conexao_wifi.cpp`
- **Purpose**: Manages WiFi connection and reconnection
- **Features**:
  - Automatic connection with timeout
  - Connection status checking
  - LCD/Serial output support

#### PainelLCD Module (`painel_lcd/`)
- **Files**: `painel_lcd.h`, `painel_lcd.cpp`
- **Purpose**: Manages LCD display output
- **Features**:
  - Support for LCD_NONE, LCD_16x2, LCD_20x4
  - Automatic line clearing
  - Float printing with error handling
  - Serial mirroring

#### SensorLDR Module (`sensores/sensor_ldr/`)
- **Files**: `sensor_ldr.h`, `sensor_ldr.cpp`
- **Purpose**: Reads light sensor data
- **Features**:
  - Raw ADC reading
  - Lux calculation with calibration coefficients
  - NAN handling for invalid readings

### 2. Created MPU6050 Sensor Class

#### MPU6050Sensor Module (`sensores/mpu6050/`)
- **Files**: `MPU6050Sensor.h`, `MPU6050Sensor.cpp`
- **Purpose**: Encapsulates all MPU6050 operations
- **Features**:
  - Initialization and connection testing
  - Calibration support
  - Separate read methods for acceleration, gyroscope, temperature
  - Vibration calculation method
  - DLPF configuration for noise reduction

**Key Methods**:
```cpp
bool begin(TwoWire& wire = Wire);
bool testConnection();
void readAcceleration();
void readGyroscope();
void readTemperature();
void readAll();
float calculateVibration(int numSamples = 100, int delayMs = 5);
```

### 3. Refactored sketch.cpp

#### New Architecture

**Primary Task** (`primaryTask()`):
- Reads all sensors (MPU6050, LDR)
- Updates display with current readings
- Handles alerts (vibration, temperature, light)
- Runs every 5 seconds (configurable)

**Secondary Task** (`secondaryTask()`):
- Checks WiFi connection
- Initializes sensor with API
- Sends sensor data to backend
- Runs in the loop when primary task is not active

**Setup**:
- Initializes all hardware (I2C, pins, LCD)
- Initializes all sensors
- Connects to WiFi
- Clean, sequential initialization

**Loop**:
- Simple timing logic
- Delegates to primary/secondary tasks
- No blocking delays
- Readable and maintainable

#### Key Improvements
1. **Separation of Concerns**: Sensor reading separated from data transmission
2. **Modular Design**: Each sensor/component in its own class
3. **Reusability**: Classes can be used in other projects
4. **Testability**: Individual modules can be tested separately
5. **Maintainability**: Easier to understand and modify
6. **Configuration**: All settings in `config.h`

### 4. Enhanced config.h

New configuration sections:
- Network and API settings
- Pin definitions
- Sensor configurations
- Timing constants

```cpp
// Network
#define NETWORK_SSID "Wokwi-GUEST"
#define NETWORK_PASSWORD ""
#define API_URL "http://localhost:8180"

// Pins
const int I2C_SDA_PIN = 21;
const int I2C_SCL_PIN = 22;
const int LDR_PIN = 34;
// ... etc

// Sensor Configuration
const float VIBRATION_THRESHOLD = 1.0;
const int VIBRATION_SAMPLES = 100;

// Timing
const unsigned long PRIMARY_TASK_INTERVAL = 5000;
const unsigned long SECONDARY_TASK_DELAY = 100;
```

## File Structure

```
src/wokwi/src/
├── api/
│   └── api.h                    # HTTP API client
├── conexao_wifi/
│   ├── conexao_wifi.h           # WiFi connection header
│   └── conexao_wifi.cpp         # WiFi connection implementation
├── painel_lcd/
│   ├── painel_lcd.h             # LCD panel header
│   └── painel_lcd.cpp           # LCD panel implementation
├── sensores/
│   ├── sensor_ldr/
│   │   ├── sensor_ldr.h         # LDR sensor header
│   │   └── sensor_ldr.cpp       # LDR sensor implementation
│   └── mpu6050/
│       ├── MPU6050Sensor.h      # MPU6050 sensor class header
│       └── MPU6050Sensor.cpp    # MPU6050 sensor class implementation
├── config.h                     # Configuration constants
├── sketch.cpp                   # Main application (refactored)
├── sketch_original.cpp          # Original sketch (backup)
├── display_manager.h            # Legacy display manager (kept for reference)
└── display_manager.cpp          # Legacy display manager (kept for reference)
```

## Migration Guide

### From Old to New Code

**Old (monolithic)**:
```cpp
// Everything in sketch.cpp
MPU6050 mpu;
void conectaWiFi() { ... }
int post_data(...) { ... }
```

**New (modular)**:
```cpp
// Separated into modules
MPU6050Sensor sensorMpu;
ConexaoWifi conexaoWifi(...);
Api api(...);
```

### Task Structure

**Old**:
```cpp
void loop() {
    // Everything happens here
    readSensors();
    sendData();
    delay(5000);
}
```

**New**:
```cpp
void primaryTask() {
    // Only sensor reading
    sensorMpu.readAll();
    sensorLdr.readLux();
    // Display updates
}

void secondaryTask() {
    // Only network operations
    if (!conexaoWifi.estaConectado()) {
        conexaoWifi.connect();
    }
    api.post_leitura(doc);
}

void loop() {
    // Timing logic
    if (time_for_primary_task) {
        primaryTask();
    } else {
        secondaryTask();
    }
}
```

## Benefits

1. **Code Organization**: Clear separation of responsibilities
2. **Reusability**: Each module can be used independently
3. **Testability**: Individual components can be tested in isolation
4. **Scalability**: Easy to add new sensors or features
5. **Maintainability**: Changes to one module don't affect others
6. **Documentation**: Each module is self-documenting
7. **Debugging**: Easier to identify and fix issues

## LCD Support

The system now supports three LCD configurations:

1. **LCD_NONE**: No physical LCD, output only to Serial
2. **LCD_16x2**: 16 columns × 2 rows display
3. **LCD_20x4**: 20 columns × 4 rows display

Select in `config.h`:
```cpp
const LcdType SELECTED_LCD = LCD_16x2;  // or LCD_20x4 or LCD_NONE
```

## Future Enhancements

Possible improvements:
1. FreeRTOS tasks for true multitasking
2. Queue-based communication between tasks
3. Power management
4. OTA updates
5. Web configuration portal
6. MQTT support
7. Data logging to SD card

## Compilation

### PlatformIO
```bash
cd src/wokwi
pio run
```

### Arduino IDE
1. Open `sketch.cpp`
2. Install libraries:
   - ArduinoJson (7.4.1+)
   - MPU6050 (1.4.3+)
   - LiquidCrystal_I2C (1.1.4+)
3. Select board: ESP32 Dev Module
4. Compile and upload

## Testing

1. **Unit Testing**: Test each module independently
2. **Integration Testing**: Test module interactions
3. **Hardware Testing**: Test on actual ESP32 hardware
4. **Wokwi Simulation**: Test in Wokwi simulator

## Original Code

The original monolithic sketch is preserved in `sketch_original.cpp` for reference.

## Credits

Based on the architecture from:
- Source project: https://github.com/Hinten/fiap_fase5_cap1
- Modules ported from: `src/ir_alem_2/esp32/src`

## License

Same as the original project.
