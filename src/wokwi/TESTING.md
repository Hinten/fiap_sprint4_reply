# Testing Guide for ESP32 Refactored Code

## Prerequisites

1. **Wokwi Simulator** (https://wokwi.com)
2. **PlatformIO** (optional, for local compilation)
3. **Arduino IDE** (alternative to PlatformIO)

## Quick Start - Wokwi Simulation

### Step 1: Upload to Wokwi
1. Go to https://wokwi.com/projects/new/esp32
2. Copy all files from `src/wokwi/src/` to the Wokwi project
3. Ensure the file structure matches:
   ```
   sketch.cpp
   config.h
   api/api.h
   conexao_wifi/conexao_wifi.h
   conexao_wifi/conexao_wifi.cpp
   painel_lcd/painel_lcd.h
   painel_lcd/painel_lcd.cpp
   sensores/sensor_ldr/sensor_ldr.h
   sensores/sensor_ldr/sensor_ldr.cpp
   sensores/mpu6050/MPU6050Sensor.h
   sensores/mpu6050/MPU6050Sensor.cpp
   ```

### Step 2: Configure Libraries
Add to `wokwi.toml`:
```toml
[wokwi]
version = 1

[[wokwi.libs]]
name = "ArduinoJson"

[[wokwi.libs]]
name = "MPU6050"

[[wokwi.libs]]
name = "LiquidCrystal I2C"
```

Or add to `libraries.txt`:
```
ArduinoJson
MPU6050
LiquidCrystal I2C
```

### Step 3: Configure diagram.json
Use the existing `diagram.json` or create a minimal one:

```json
{
  "version": 1,
  "author": "Your Name",
  "editor": "wokwi",
  "parts": [
    { "type": "wokwi-esp32-devkit-v1", "id": "esp", "top": 0, "left": 0 },
    { "type": "wokwi-mpu6050", "id": "mpu1", "top": 100, "left": 200 },
    { "type": "wokwi-lcd2004", "id": "lcd1", "top": 100, "left": -200 },
    { "type": "wokwi-photoresistor-sensor", "id": "ldr1", "top": 250, "left": 100 }
  ],
  "connections": [
    ["esp:GND", "mpu1:GND", "black"],
    ["esp:3V3", "mpu1:VCC", "red"],
    ["esp:21", "mpu1:SDA", "green"],
    ["esp:22", "mpu1:SCL", "blue"],
    ["esp:GND", "lcd1:GND", "black"],
    ["esp:5V", "lcd1:VCC", "red"],
    ["esp:21", "lcd1:SDA", "green"],
    ["esp:22", "lcd1:SCL", "blue"],
    ["esp:34", "ldr1:DO", "yellow"],
    ["esp:3V3", "ldr1:VCC", "red"],
    ["esp:GND", "ldr1:GND", "black"]
  ]
}
```

### Step 4: Run Simulation
1. Click "Start Simulation" in Wokwi
2. Open Serial Monitor
3. Observe:
   - Initialization messages
   - WiFi connection (to Wokwi-GUEST)
   - MPU6050 sensor readings
   - LDR readings
   - LCD display output

## Expected Output

### Serial Monitor
```
=== ESP32 Industrial Monitor ===
Version 2.0 - Modular Architecture
=== Display Manager Initialized ===
LCD Mode: 16x2
LCD initialized successfully
Sensor LDR initialized
MPU6050 connected successfully
Conectando ao WiFi
...
WiFi conectado!
IP: 192.168.1.2
Iniciando sensor...
Sensor iniciado com sucesso na API
Chip ID: XXXXXXXXXXXX

[LCD 0,0] Temp: 25.3 C
[LCD 0,1] Lux: 450 (Escuro)
Temp: 25.30 | Lux: 450 | Vib: 0.05 | Accel X:0.01 Y:0.02 Z:1.00
Dados enviados com sucesso!
```

### LCD Display
```
Line 0: Temp: 25.3 C
Line 1: Lux: 450 (Escuro)
```

After 1 second:
```
Line 0: Vib: 0.05
Line 1: Vibracao normal
```

## Testing Different Configurations

### Test 1: LCD_NONE (Serial Only)
In `config.h`, change:
```cpp
const LcdType SELECTED_LCD = LCD_NONE;
```
Expected: All output goes to Serial, no LCD initialization.

### Test 2: LCD_20x4 (Larger Display)
In `config.h`, change:
```cpp
const LcdType SELECTED_LCD = LCD_20x4;
```
Update `diagram.json` to use `wokwi-lcd2004` (20x4 display).
Expected: More information displayed, including accelerometer on lines 2-3.

### Test 3: Vibration Alert
Shake the MPU6050 sensor in Wokwi (if supported) or modify the threshold:
```cpp
const float VIBRATION_THRESHOLD = 0.01;  // Lower threshold
```
Expected: Vibration alert triggered, buzzer/LED activated.

### Test 4: Temperature Alert
Modify temperature reading (in simulation) or change threshold:
```cpp
if (sensorData.temperature > 25.0) {  // Lower threshold for testing
```
Expected: Temperature alert triggered.

### Test 5: Light Threshold
Cover/uncover the LDR sensor in Wokwi.
Expected: Display switches between "Escuro" and "Claro", LED/buzzer activates.

## Troubleshooting

### Issue: "MPU6050 connection failed!"
**Solution**: Check I2C connections in diagram.json (SDA=21, SCL=22)

### Issue: "WiFi desconectado"
**Solution**: Ensure Wokwi WiFi is enabled (should connect automatically to Wokwi-GUEST)

### Issue: "Compilation error: file not found"
**Solution**: Ensure all module files are uploaded and paths are correct

### Issue: "LCD not displaying"
**Solution**: 
1. Check LCD I2C address (default 0x27)
2. Verify LCD type matches config.h
3. Check I2C wiring

### Issue: "No sensor readings"
**Solution**: 
1. Verify sensor initialization in Serial Monitor
2. Check pin definitions in config.h
3. Ensure sensors are connected in diagram.json

## Local Compilation (PlatformIO)

### Install PlatformIO
```bash
pip install platformio
```

### Build and Upload
```bash
cd src/wokwi
pio run
pio run --target upload
```

### Monitor Serial
```bash
pio device monitor
```

## Local Compilation (Arduino IDE)

### Install Libraries
1. Open Arduino IDE
2. Go to Tools → Manage Libraries
3. Install:
   - ArduinoJson (7.4.1+)
   - MPU6050 by Electronic Cats (1.4.3+)
   - LiquidCrystal I2C (1.1.4+)

### Configure Board
1. Select: Tools → Board → ESP32 Arduino → ESP32 Dev Module
2. Select correct COM port

### Compile and Upload
1. Open `sketch.cpp`
2. Click Verify (checkmark icon)
3. Click Upload (arrow icon)

## Testing Checklist

- [ ] Code compiles without errors
- [ ] Serial output shows initialization
- [ ] WiFi connects successfully
- [ ] MPU6050 initializes and reads data
- [ ] LDR reads light values
- [ ] LCD displays correctly (or Serial if LCD_NONE)
- [ ] Primary task executes every 5 seconds
- [ ] Secondary task sends data to API
- [ ] Alerts trigger on thresholds
- [ ] Buzzer and LED work
- [ ] Modular structure allows easy modification

## Next Steps

1. **Test on Real Hardware**: Upload to actual ESP32 with sensors
2. **Customize**: Modify thresholds, intervals in config.h
3. **Extend**: Add new sensors using the modular pattern
4. **Deploy**: Connect to production API endpoint
5. **Monitor**: Use cloud dashboard to view data

## Advanced Testing

### Test Module Independence
Test each module separately:

```cpp
// Test LDR only
void loop() {
    Serial.println(sensorLdr.readLux());
    delay(1000);
}
```

### Test Tasks Separately
Comment out one task to verify independence:

```cpp
void loop() {
    // primaryTask();  // Comment this out
    secondaryTask();
}
```

### Memory Testing
Monitor heap usage:

```cpp
void loop() {
    Serial.print("Free heap: ");
    Serial.println(ESP.getFreeHeap());
    // ... normal loop code
}
```

## Performance Metrics

Expected performance on ESP32:
- **Boot time**: ~2-3 seconds
- **Primary task execution**: ~500ms (including vibration calculation)
- **Secondary task cycle**: ~100ms
- **WiFi connection**: ~5-10 seconds
- **API request**: ~200-500ms
- **Total cycle time**: ~5 seconds
- **Memory usage**: ~50-60KB (out of 320KB)

## Support

For issues or questions:
1. Check REFACTORING.md for architecture details
2. Check COMPARISON.md for code examples
3. Review ARCHITECTURE.md for module interactions
4. Run validate_structure.sh to verify file structure
5. Check original code in sketch_original.cpp

## License

Same as original project.
