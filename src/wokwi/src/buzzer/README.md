# BuzzerLed Class - Guia de Uso

## Visão Geral

A classe `BuzzerLed` controla três componentes de hardware:
- **Buzzer**: Para alertas sonoros e melodias
- **LED**: Para indicações visuais
- **Relé**: Para controle de carga externa

## Inicialização

```cpp
#include "buzzer/buzzer.h"

// Pinos padrão (config.h)
const int BUZZER_PIN = 25;
const int LED_PIN = 15;
const int RELAY_PIN = 32;

// Criar instância
BuzzerLed buzzer(BUZZER_PIN, LED_PIN, RELAY_PIN);

void setup() {
    // Inicializar pinos
    buzzer.setup();
    
    // Tocar melodia de inicialização
    buzzer.playStartupTune();
}
```

## Métodos Principais

### Alertas

```cpp
// Alerta combinado (buzzer + LED)
// Parâmetros: repetições, frequência(Hz), duração(ms)
buzzer.alertaBuzzerLed(3, 1000, 300);

// Desligar tudo
buzzer.turnOff();
```

### Buzzer - Tons Básicos

```cpp
// Tocar um tom
buzzer.playTone(440, 500);  // 440Hz por 500ms

// Parar o som
buzzer.stopTone();

// Beeps rápidos
buzzer.beep();        // 1 beep
buzzer.doubleBeep();  // 2 beeps

// Sirene
buzzer.siren(2000);   // Sirene por 2 segundos
```

### Buzzer - Melodias

```cpp
// Melodia de startup (rápida)
buzzer.playStartupTune();

// Super Mario Bros
buzzer.playMarioTune();

// Star Wars (Imperial March)
buzzer.playStarWarsTune();

// Happy Birthday
buzzer.playHappyBirthday();
```

### LED - Controle Básico

```cpp
// Ligar/desligar
buzzer.ledOn();
buzzer.ledOff();
buzzer.ledToggle();

// Piscar
buzzer.ledBlink(3, 200, 200);  // 3x, 200ms on, 200ms off

// Ajustar brilho (0-255, requer PWM)
buzzer.ledSetBrightness(128);  // Brilho médio
```

### LED - Efeitos Especiais

```cpp
// Efeito de pulso (fade in/out)
buzzer.ledPulse(3, 1000);  // 3 ciclos, 1s por ciclo

// Efeito de respiração
buzzer.ledBreathe(5);  // 5 respirações

// SOS em código Morse
buzzer.ledSOS();

// Batimento cardíaco
buzzer.ledHeartbeat(3);  // 3 batimentos
```

### Relé - Controle

```cpp
// Ligar/desligar
buzzer.relayOn();
buzzer.relayOff();
buzzer.relayToggle();

// Verificar estado
if (buzzer.relayState()) {
    // Relé está ligado
}

// Pulso (liga e desliga)
buzzer.relayPulse(1000);  // Liga por 1 segundo
```

### Efeitos Combinados

```cpp
// Celebração (LED + buzzer + relé)
buzzer.celebrate();

// Alerta crítico
buzzer.criticalAlert();

// Efeito de sucesso
buzzer.successEffect();
```

## Exemplos de Uso

### Alerta de Temperatura Alta

```cpp
if (temperatura > 70.0) {
    painel.printLCDSerial(0, 1, "#ALERTA: >70 C#");
    buzzer.alertaBuzzerLed(3, 1500, 300);
}
```

### Alerta de Vibração

```cpp
if (vibracao > LIMIAR_VIBRACAO) {
    painel.printLCDSerial(0, 1, "#ALERTA VIBRACAO#");
    buzzer.alertaBuzzerLed(3, 1000, 300);
}
```

### Indicação de Luminosidade

```cpp
if (lux < 500) {
    // Ambiente escuro - desliga tudo
    buzzer.turnOff();
} else {
    // Ambiente claro - alerta
    buzzer.alertaBuzzerLed(3, 1000, 300);
}
```

### WiFi Desconectado

```cpp
if (!conexaoWifi.estaConectado()) {
    buzzer.alertaBuzzerLed(2, 2000, 500);
    Serial.println("WiFi desconectado!");
}
```

### Celebração de Inicialização

```cpp
void setup() {
    buzzer.setup();
    
    // Toca melodia de boas-vindas
    buzzer.playMarioTune();
    
    // Ou celebra com efeitos
    buzzer.celebrate();
}
```

## Notas Musicais Disponíveis

A biblioteca inclui definições de notas de B0 até D8:

```cpp
// Exemplos de notas
NOTE_C4  // Dó central (262 Hz)
NOTE_E4  // Mi (330 Hz)
NOTE_G4  // Sol (392 Hz)
NOTE_A4  // Lá (440 Hz - padrão de afinação)
NOTE_C5  // Dó agudo (523 Hz)

REST     // Silêncio (0 Hz)
```

## Criando Melodias Personalizadas

```cpp
void playCustomMelody() {
    // Array de notas
    int melody[] = {NOTE_C4, NOTE_E4, NOTE_G4, NOTE_C5};
    int durations[] = {200, 200, 200, 400};
    
    for (int i = 0; i < 4; i++) {
        buzzer.playTone(melody[i], durations[i]);
        delay(50);  // Pausa entre notas
    }
}
```

## Considerações Técnicas

### ESP32
- O buzzer usa PWM via `ledcSetup()` e `ledcWriteTone()`
- O LED pode usar PWM para controle de brilho
- Todos os pinos GPIO podem ser usados

### Arduino
- O buzzer usa `tone()` e `noTone()`
- O LED usa `analogWrite()` em pinos PWM
- Pinos PWM típicos: 3, 5, 6, 9, 10, 11

### Relé
- **ATENÇÃO**: Relés controlam cargas de alta potência
- Certifique-se de usar um módulo relé apropriado
- Use proteção de circuito adequada
- Em simulação (Wokwi), funciona como switch virtual

## Mapeamento de Pinos (Wokwi)

De acordo com `diagram.json` e `config.h`:

| Componente | Pino ESP32 | Tipo |
|------------|------------|------|
| Buzzer     | 25         | PWM  |
| LED        | 15         | GPIO |
| Relé       | 32         | GPIO |
| LDR        | 34         | ADC  |
| MPU6050    | 21, 22     | I2C  |
| LCD        | 21, 22     | I2C  |

## Troubleshooting

### Buzzer não toca
- Verifique se `setup()` foi chamado
- Confirme o pino do buzzer (25)
- Teste com `beep()` simples

### LED não acende
- Verifique polaridade (ânodo no pino, cátodo no GND)
- Confirme o pino do LED (15)
- Use resistor apropriado (220-330Ω)

### Relé não ativa
- Verifique alimentação do módulo relé
- Confirme o pino do relé (32)
- Teste com `relayToggle()`

### Efeitos PWM não funcionam
- Confirme que o pino suporta PWM
- No ESP32, quase todos os pinos suportam PWM
- No Arduino, use pinos PWM específicos (3, 5, 6, 9, 10, 11)

## Licença

Este código faz parte do projeto FIAP Sprint 4 - Sistema de Manutenção Preditiva Industrial.
