# Code Comparison: Before and After Refactoring

## Overview
This document shows side-by-side comparisons of the old monolithic code versus the new modular architecture.

## 1. WiFi Connection

### Before (in sketch.cpp)
```cpp
// === FUNÇÃO DE CONEXÃO WI-FI ===
void conectaWiFi() {
  WiFi.begin(ssid, password, canal_wifi);
  displayPrint("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  displayPrint("WiFi conectado!");
}
```

### After (conexao_wifi/conexao_wifi.cpp)
```cpp
class ConexaoWifi {
    // ... member variables ...
    
    void connect() {
        WiFi.begin(ssid, password);
        print_serial_or_lcd("Conectando ao WiFi");
        
        const unsigned long inicio = millis();
        conectado = false;
        
        while (WiFi.status() != WL_CONNECTED && 
               (millis() - inicio) < tempoMaximoConexao) {
            delay(500);
            Serial.print(".");
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            print_serial_or_lcd("WiFi conectado!");
            conectado = true;
        } else {
            print_serial_or_lcd("Falha ao conectar!");
            conectado = false;
        }
    }
    
    bool estaConectado() {
        conectado = (WiFi.status() == WL_CONNECTED);
        return conectado;
    }
};
```

**Benefits**:
- Timeout support prevents infinite loops
- Status checking method
- Encapsulated state management
- Reusable across projects

---

## 2. API Communication

### Before (in sketch.cpp)
```cpp
int post_data(JsonDocument& doc, const String& endpoint_api) {
  Serial.println("Enviando dados para a API: " + endpoint_api);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(endpoint_api);

    String jsonStr;
    serializeJson(doc, jsonStr);
    int httpCode = http.POST(jsonStr);

    if (httpCode > 0) {
      Serial.println("Status code: " + String(httpCode));
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.println("Erro na requisição");
    }
    http.end();
    return httpCode;
  } else {
    Serial.println("WiFi desconectado, impossível fazer requisição!");
  }
  return -1;
}
```

### After (api/api.h)
```cpp
class Api {
    // ... member variables ...
    
    Response post_json(const String& path, const JsonDocument& json) {
        String jsonStr;
        serializeJson(json, jsonStr);
        return post(path, jsonStr, "application/json");
    }

    Response post_init() {
        JsonDocument doc;
        doc["serial"] = chipIdStr;
        return post_json(initUrl, doc);
    }

    Response post_leitura(JsonDocument& json) {
        json["serial"] = chipIdStr;
        return post_json(leituraUrl, json);
    }
};

struct Response {
    const int status_code;
    const String body;

    JsonDocument toJson() const {
        JsonDocument doc;
        const DeserializationError error = deserializeJson(doc, body);
        if (error) {
            return JsonDocument(nullptr);
        }
        return doc;
    }
};
```

**Benefits**:
- Structured response with JSON parsing
- Automatic chip ID injection
- Dedicated methods for each endpoint
- Error handling with Response struct
- Testable and mockable

---

## 3. MPU6050 Sensor

### Before (in sketch.cpp)
```cpp
MPU6050 mpu;

void setup() {
  Wire.begin(21, 22);
  mpu.initialize();
  while (!mpu.testConnection()) {
    displayPrint("MPU6050 nao conectado!");
    delay(1000);
  }
}

void loop() {
  // Read temperature
  int rawTemp = mpu.getTemperature();
  float tempC = rawTemp / 340.0 + 36.53;
  
  // Read acceleration
  int16_t ax_raw, ay_raw, az_raw;
  mpu.getAcceleration(&ax_raw, &ay_raw, &az_raw);
  float ax = ax_raw / 16384.0;
  float ay = ay_raw / 16384.0;
  float az = az_raw / 16384.0;
  
  // Read gyroscope
  int16_t gx_raw, gy_raw, gz_raw;
  mpu.getRotation(&gx_raw, &gy_raw, &gz_raw);
  float gx = gx_raw / 131.0;
  float gy = gy_raw / 131.0;
  float gz = gz_raw / 131.0;
  
  // Calculate vibration
  float somaVibracao = 0;
  for (int i = 0; i < NUM_AMOSTRAS; i++) {
    float modulo = sqrt(ax * ax + ay * ay + az * az);
    float vibracao = abs(modulo - 1.0);
    somaVibracao += vibracao;
    delay(5);
  }
  vibracaoMedia = somaVibracao / NUM_AMOSTRAS;
}
```

### After (sensores/mpu6050/MPU6050Sensor.cpp)
```cpp
class MPU6050Sensor {
    MPU6050 mpu;
    float ax, ay, az, gx, gy, gz, temperature;
    
public:
    bool begin(TwoWire& wire = Wire) {
        mpu.initialize();
        initialized = mpu.testConnection();
        
        if (initialized) {
            mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
            mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);
            setDLPF(MPU6050_DLPF_BW_20);
        }
        return initialized;
    }
    
    void readAll() {
        readAcceleration();
        readGyroscope();
        readTemperature();
    }
    
    float calculateVibration(int numSamples = 100, int delayMs = 5) {
        float somaVibracao = 0.0;
        
        for (int i = 0; i < numSamples; i++) {
            int16_t ax_raw, ay_raw, az_raw;
            mpu.getAcceleration(&ax_raw, &ay_raw, &az_raw);
            
            float ax_g = ax_raw / 16384.0;
            float ay_g = ay_raw / 16384.0;
            float az_g = az_raw / 16384.0;
            
            float modulo = sqrt(ax_g * ax_g + ay_g * ay_g + az_g * az_g);
            float vibracao = abs(modulo - 1.0);
            somaVibracao += vibracao;
            
            if (delayMs > 0) delay(delayMs);
        }
        
        return somaVibracao / numSamples;
    }
    
    // Getters
    float getAx() const { return ax; }
    float getTemperature() const { return temperature; }
    // ...
};
```

**Benefits**:
- Encapsulated sensor state
- Calibration support
- Dedicated methods for each reading type
- Vibration calculation as a method
- Configuration methods (DLPF, ranges)
- Testable without hardware

---

## 4. Main Loop Structure

### Before (sketch.cpp - monolithic)
```cpp
void loop() {
  if (!iniciou_sensor) {
    iniciar_sensor();
  }

  JsonDocument doc;
  doc["serial"] = chipidStr;

  // Read LDR
  int ldrValue = analogRead(LDR_PIN);
  int lux = map(ldrValue, 0, 4095, 0, 2000);
  doc["lux"] = lux;

  // Read temperature
  int rawTemp = mpu.getTemperature();
  float tempC = rawTemp / 340.0 + 36.53;
  doc["temperatura"] = tempC;
  
  // ... 200+ more lines of sensor reading, display, alerts ...
  
  if (iniciou_sensor) {
    int httpcode = post_data(doc, post_sensor);
    if (httpcode >= 200 && httpcode < 300) {
      Serial.println(F("Dados enviados com sucesso!"));
    }
  }

  delay(5000);
}
```

### After (sketch.cpp - modular)
```cpp
struct SensorData {
    float temperature;
    float lux;
    float accelX, accelY, accelZ;
    float gyroX, gyroY, gyroZ;
    float vibration;
} sensorData;

void primaryTask() {
    // Read all sensors
    sensorMpu.readTemperature();
    sensorData.temperature = sensorMpu.getTemperature();
    
    sensorData.lux = sensorLdr.readLux();
    
    sensorMpu.readAcceleration();
    sensorData.accelX = sensorMpu.getAx();
    // ...
    
    sensorData.vibration = sensorMpu.calculateVibration(VIBRATION_SAMPLES, 5);
    
    // Display and alerts
    displaySensorReadings();
    checkAlerts();
}

void secondaryTask() {
    // Network operations
    if (!conexaoWifi.estaConectado()) {
        conexaoWifi.connect();
        return;
    }
    
    if (!sensorIniciado) {
        iniciarSensor();
        return;
    }
    
    // Send data
    JsonDocument doc;
    doc["temperatura"] = sensorData.temperature;
    doc["lux"] = sensorData.lux;
    // ...
    
    Response response = api.post_leitura(doc);
    if (response.status_code >= 200 && response.status_code < 300) {
        Serial.println(F("Dados enviados com sucesso!"));
    }
}

void loop() {
    unsigned long agora = millis();
    
    if (agora - ultimoMillis >= PRIMARY_TASK_INTERVAL) {
        ultimoMillis = agora;
        primaryTask();
    } else {
        secondaryTask();
        delay(SECONDARY_TASK_DELAY);
    }
}
```

**Benefits**:
- Clear separation: sensors vs network
- Non-blocking: secondary task runs frequently
- Structured data with SensorData struct
- Configurable timing
- Easier to debug and test
- Can evolve to FreeRTOS tasks

---

## 5. Configuration

### Before (hardcoded in sketch.cpp)
```cpp
const char* ssid = NETWORK_SSID;
const char* password = NETWORK_PASSWORD;
const int canal_wifi = 6;
const char* endpoint_api = API_URL;
const String init_sensor = String(endpoint_api) + "/init/";
const String post_sensor = String(endpoint_api) + "/leitura/";

const int LDR_PIN = 34;
const int RELAY_PIN = 32;
const int LED_PIN = 15;
const int BUZZER_PIN = 2;

const int NUM_AMOSTRAS = 100;
const float LIMIAR_VIBRACAO = 1.0;
```

### After (config.h - centralized)
```cpp
// Network and API
#define NETWORK_SSID "Wokwi-GUEST"
#define NETWORK_PASSWORD ""
#define API_URL "http://localhost:8180"
#define API_BASE_URL API_URL
#define API_INIT_URL "/init/"
#define API_LEITURA_URL "/leitura/"

// Pins
const int I2C_SDA_PIN = 21;
const int I2C_SCL_PIN = 22;
const int LDR_PIN = 34;
const int RELAY_PIN = 32;
const int LED_PIN = 15;
const int BUZZER_PIN = 2;

// Sensor Configuration
const float LDR_VCC = 3.3;
const float LDR_RESISTOR = 10000.0;
const float VIBRATION_THRESHOLD = 1.0;
const int VIBRATION_SAMPLES = 100;

// Timing
const unsigned long PRIMARY_TASK_INTERVAL = 5000;
const unsigned long SECONDARY_TASK_DELAY = 100;

// LCD
enum LcdType { LCD_NONE, LCD_16x2, LCD_20x4 };
const LcdType SELECTED_LCD = LCD_16x2;
```

**Benefits**:
- All configuration in one place
- Easy to change without searching code
- Compile-time constants for optimization
- Documented with comments
- Type-safe enums

---

## Summary of Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Lines in sketch.cpp** | 300 | 250 |
| **Number of files** | 4 | 14 |
| **Modularity** | Monolithic | Modular |
| **Reusability** | Low | High |
| **Testability** | Difficult | Easy |
| **Maintainability** | Hard | Easy |
| **LCD Support** | Fixed | 3 modes |
| **Configuration** | Scattered | Centralized |
| **Network Handling** | Blocking | Managed |
| **Sensor Code** | Inline | Encapsulated |

## Lines of Code Breakdown

### Before
- sketch.cpp: ~300 lines (everything)

### After
- sketch.cpp: ~250 lines (orchestration)
- api.h: ~120 lines
- conexao_wifi.h/cpp: ~80 lines
- painel_lcd.h/cpp: ~150 lines
- sensor_ldr.h/cpp: ~50 lines
- mpu6050.h/cpp: ~160 lines
- config.h: ~70 lines

**Total**: ~880 lines (vs 300), but:
- Much better organized
- Highly reusable
- Easier to maintain
- Better documentation
- Separation of concerns
