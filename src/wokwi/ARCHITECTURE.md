# ESP32 Modular Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         sketch.cpp                               │
│                      (Main Application)                          │
│                                                                   │
│  ┌──────────────┐                  ┌───────────────┐            │
│  │ setup()      │                  │   loop()      │            │
│  │              │                  │               │            │
│  │ - Init I2C   │                  │ - Timing      │            │
│  │ - Init LCD   │                  │ - Dispatch    │            │
│  │ - Init WiFi  │                  │   tasks       │            │
│  │ - Init MPU   │                  └───────┬───────┘            │
│  │ - Init LDR   │                          │                    │
│  └──────────────┘                          │                    │
│                                             │                    │
│         ┌───────────────────────────────────┼──────────┐        │
│         │                                   │          │        │
│         ▼                                   ▼          │        │
│  ┌──────────────┐                  ┌───────────────┐  │        │
│  │ primaryTask()│                  │secondaryTask()│  │        │
│  │              │                  │               │  │        │
│  │ Read Sensors │                  │ Check WiFi    │  │        │
│  │ Update LCD   │                  │ Init Sensor   │  │        │
│  │ Handle       │                  │ Send Data     │  │        │
│  │ Alerts       │                  │               │  │        │
│  └──────┬───────┘                  └───────┬───────┘  │        │
│         │                                   │          │        │
└─────────┼───────────────────────────────────┼──────────┼────────┘
          │                                   │          │
          │ Uses                              │ Uses     │
          ▼                                   ▼          ▼
┌─────────────────────┐         ┌──────────────────────────────┐
│   Sensor Modules    │         │     Network Modules          │
│                     │         │                              │
│ ┌─────────────────┐ │         │ ┌──────────────────────────┐ │
│ │ MPU6050Sensor   │ │         │ │    ConexaoWifi           │ │
│ │                 │ │         │ │                          │ │
│ │ - begin()       │ │         │ │ - setup()                │ │
│ │ - readAll()     │ │         │ │ - connect()              │ │
│ │ - readAccel()   │ │         │ │ - estaConectado()        │ │
│ │ - readGyro()    │ │         │ └────────────┬─────────────┘ │
│ │ - readTemp()    │ │         │              │               │
│ │ - calcVibration│ │         │              │ Uses          │
│ └─────────────────┘ │         │              ▼               │
│                     │         │ ┌──────────────────────────┐ │
│ ┌─────────────────┐ │         │ │         Api              │ │
│ │   SensorLDR     │ │         │ │                          │ │
│ │                 │ │         │ │ - post_init()            │ │
│ │ - setup()       │ │         │ │ - post_leitura()         │ │
│ │ - readLux()     │ │         │ │ - get()                  │ │
│ │ - readRaw()     │ │         │ │ - post_json()            │ │
│ └─────────────────┘ │         │ └──────────────────────────┘ │
└─────────────────────┘         └──────────────────────────────┘
          │                                   │
          │ Uses                              │ Uses
          ▼                                   ▼
┌─────────────────────┐         ┌──────────────────────────────┐
│   Display Module    │         │    External Services         │
│                     │         │                              │
│ ┌─────────────────┐ │         │ ┌──────────────────────────┐ │
│ │   PainelLCD     │ │         │ │   WiFi Network           │ │
│ │                 │ │         │ └──────────────────────────┘ │
│ │ - setup()       │ │         │ ┌──────────────────────────┐ │
│ │ - printLCD...() │ │         │ │   Backend API            │ │
│ │ - clear()       │ │         │ │   (HTTP REST)            │ │
│ │ - LCD_NONE      │ │         │ └──────────────────────────┘ │
│ │ - LCD_16x2      │ │         └──────────────────────────────┘
│ │ - LCD_20x4      │ │
│ └─────────────────┘ │
└─────────────────────┘

═══════════════════════════════════════════════════════════════

Configuration Layer (config.h)
┌─────────────────────────────────────────────────────────────┐
│ • Network Settings (SSID, Password, API URL)                 │
│ • Pin Definitions (I2C, LDR, LED, Buzzer, Relay)            │
│ • Sensor Configuration (Thresholds, Samples)                │
│ • Timing Constants (Task Intervals)                         │
│ • LCD Type Selection (NONE, 16x2, 20x4)                     │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Sensors → primaryTask() → SensorData struct
                              │
                              ▼
                    Display on LCD/Serial
                              │
                              ▼
                    secondaryTask() → JSON → API → Backend

WiFi Connection ←─── secondaryTask()
      │                     │
      └─────────────────────┘
```

## Task Timing

```
Time →

Primary Task:  |─────5s─────X─────5s─────X─────5s─────X
               Read sensors   Read sensors   Read sensors

Secondary:     XXXXXXXXXXXXX|XXXXXXXXXXXXX|XXXXXXXXXXXXX
               Check WiFi    Send data     Check WiFi
               Send data     Check WiFi    Send data
               (100ms loop)  (100ms loop)  (100ms loop)
```

## Module Dependencies

```
sketch.cpp
  ├── config.h
  ├── painel_lcd/ ────┐
  ├── conexao_wifi/ ──┼─→ painel_lcd/
  ├── api/ ───────────┼─→ conexao_wifi/
  ├── sensor_ldr/     │
  └── mpu6050/        │
                      │
                      └── (forward declaration)
```

## Comparison: Old vs New

### Old Architecture (Monolithic)
```
sketch.cpp (300 lines)
├── WiFi functions
├── API functions
├── MPU6050 code inline
├── LDR reading inline
├── Display code inline
└── Everything in loop()
```

### New Architecture (Modular)
```
src/
├── config.h              (Centralized config)
├── sketch.cpp            (Clean, 250 lines)
├── api/                  (HTTP client)
├── conexao_wifi/         (WiFi management)
├── painel_lcd/           (Display abstraction)
├── sensores/
│   ├── sensor_ldr/       (LDR encapsulation)
│   └── mpu6050/          (MPU6050 class)
└── [legacy files]
```

## Benefits

1. **Modularity**: Each component is self-contained
2. **Reusability**: Modules can be used in other projects
3. **Testability**: Individual modules can be tested
4. **Maintainability**: Easy to update one module
5. **Readability**: Clear separation of concerns
6. **Scalability**: Easy to add new sensors/features
