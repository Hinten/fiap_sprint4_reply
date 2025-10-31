# Arquitetura da Classe BuzzerLed

```
┌─────────────────────────────────────────────────────────────┐
│                      BuzzerLed Class                        │
│                                                             │
│  Controla 3 componentes de hardware:                       │
│  • Buzzer (pino 25)                                         │
│  • LED    (pino 15)                                         │
│  • Relé   (pino 32)                                         │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│  Buzzer Control  │ │   LED Control    │ │  Relay Control  │
├──────────────────┤ ├──────────────────┤ ├─────────────────┤
│ • playTone()     │ │ • ledOn()        │ │ • relayOn()     │
│ • stopTone()     │ │ • ledOff()       │ │ • relayOff()    │
│ • beep()         │ │ • ledToggle()    │ │ • relayToggle() │
│ • doubleBeep()   │ │ • ledBlink()     │ │ • relayState()  │
│ • siren()        │ │ • ledPulse()     │ │ • relayPulse()  │
│                  │ │ • ledBreathe()   │ │                 │
│ Melodias:        │ │ • ledSetBright() │ └─────────────────┘
│ • playStartup()  │ │ • ledSOS()       │
│ • playMario()    │ │ • ledHeartbeat() │
│ • playStarWars() │ │                  │
│ • playHappyBD()  │ └──────────────────┘
└──────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Efeitos Combinados                             │
├─────────────────────────────────────────────────────────────┤
│ • alertaBuzzerLed() - Alerta com buzzer + LED              │
│ • celebrate()       - Celebração (todos os componentes)     │
│ • criticalAlert()   - Alerta crítico (buzzer + LED)        │
│ • successEffect()   - Efeito de sucesso (buzzer + LED)     │
│ • turnOff()         - Desliga buzzer + LED                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Uso no sketch.cpp                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BuzzerLed buzzer(BUZZER_PIN, LED_PIN, RELAY_PIN);        │
│                                                             │
│  void setup() {                                             │
│      buzzer.setup();                 // Inicializa pinos   │
│      buzzer.playStartupTune();       // Melodia startup    │
│  }                                                          │
│                                                             │
│  void loop() {                                              │
│      if (lux < 500) {                                       │
│          buzzer.alertaBuzzerLed(3, 1000, 300);            │
│      }                                                      │
│                                                             │
│      if (vibracao > LIMIAR) {                              │
│          buzzer.alertaBuzzerLed(3, 1000, 300);            │
│      }                                                      │
│                                                             │
│      if (temperatura > 70.0) {                             │
│          buzzer.alertaBuzzerLed(3, 1500, 300);            │
│      }                                                      │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Hardware (Wokwi Diagram)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ESP32                                                      │
│  ├─ Pino 25 ──────────► Buzzer (wokwi-buzzer)             │
│  ├─ Pino 15 ──────────► LED (wokwi-led) + Resistor        │
│  ├─ Pino 32 ──────────► Relé (wokwi-relay-module)         │
│  ├─ Pino 34 ──────────► LDR (wokwi-photoresistor)         │
│  ├─ Pinos 21,22 ──────► I2C: MPU6050 + LCD2004            │
│  └─ GND, VCC ──────────► Alimentação                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Suporte PWM (ESP32)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Canal 0 (buzzer):  ledcSetup(0, 2000, 8)                 │
│                     ledcWriteTone(0, frequency)             │
│                                                             │
│  Canal 1 (LED):     ledcSetup(1, 5000, 8)                 │
│                     ledcWrite(1, brightness)                │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Notas Musicais Disponíveis                     │
├─────────────────────────────────────────────────────────────┤
│  NOTE_C4 (262Hz)  - Dó central                             │
│  NOTE_E4 (330Hz)  - Mi                                      │
│  NOTE_G4 (392Hz)  - Sol                                     │
│  NOTE_A4 (440Hz)  - Lá (padrão afinação)                   │
│  NOTE_C5 (523Hz)  - Dó agudo                               │
│  ...                                                        │
│  NOTE_C8 (4186Hz) - Dó super agudo                         │
│  REST    (0Hz)    - Silêncio                               │
└─────────────────────────────────────────────────────────────┘
```

## Fluxo de Execução

```
1. Inicialização (setup)
   └─► buzzer.setup()
       ├─► Configura pino do buzzer (OUTPUT + PWM)
       ├─► Configura pino do LED (OUTPUT)
       └─► Configura pino do relé (OUTPUT)

2. Melodia de startup
   └─► buzzer.playStartupTune()
       ├─► Toca NOTE_C4 (150ms)
       ├─► Toca NOTE_E4 (150ms)
       ├─► Toca NOTE_G4 (150ms)
       └─► Toca NOTE_C5 (300ms)

3. Loop principal
   └─► Monitora sensores
       ├─► Se lux < 500
       │   └─► buzzer.alertaBuzzerLed(3, 1000, 300)
       ├─► Se vibração > limiar
       │   └─► buzzer.alertaBuzzerLed(3, 1000, 300)
       └─► Se temperatura > 70°C
           └─► buzzer.alertaBuzzerLed(3, 1500, 300)

4. Alerta (alertaBuzzerLed)
   └─► Para cada repetição:
       ├─► ledOn()
       ├─► playTone(frequency, duration)
       ├─► delay(duration)
       ├─► ledOff()
       ├─► stopTone()
       └─► delay(duration)
```

## Cenários de Uso

### Alerta de Temperatura Alta
```
Temperatura > 70°C
    ↓
buzzer.alertaBuzzerLed(3, 1500, 300)
    ↓
LED pisca 3x + buzzer 1500Hz por 300ms cada
```

### Alerta de Vibração
```
Vibração > limiar
    ↓
buzzer.alertaBuzzerLed(3, 1000, 300)
    ↓
LED pisca 3x + buzzer 1000Hz por 300ms cada
```

### Ambiente Escuro
```
Luminosidade < 500 lux
    ↓
buzzer.alertaBuzzerLed(3, 1000, 300)
    ↓
LED pisca 3x + buzzer 1000Hz por 300ms cada
```

### WiFi Desconectado
```
WiFi offline
    ↓
buzzer.alertaBuzzerLed(2, 2000, 500)
    ↓
LED pisca 2x + buzzer 2000Hz por 500ms cada
```

## Arquivos do Projeto

```
src/wokwi/src/buzzer/
├── buzzer.h          # Header com declarações da classe
├── buzzer.cpp        # Implementação dos métodos
├── README.md         # Guia de uso completo
├── exemplo.cpp       # Exemplos de uso
└── ARCHITECTURE.md   # Este arquivo (arquitetura)
```
