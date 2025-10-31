#include "buzzer.h"

// ========== CONSTRUTOR E SETUP ==========

BuzzerLed::BuzzerLed(int pinBuzzer, int pinLed, int pinRelay)
    : _pinBuzzer(pinBuzzer), _pinLed(pinLed), _pinRelay(pinRelay),
      _relayState(false), _ledState(false), _ledPwmConfigured(false) {
}

void BuzzerLed::setup() {
    // Configura pino do buzzer
    if (_pinBuzzer >= 0) {
        pinMode(_pinBuzzer, OUTPUT);
        // Configura PWM para o buzzer (ESP32)
        #ifdef ESP32
        ledcSetup(_pwmChannel, 2000, _pwmResolution);
        ledcAttachPin(_pinBuzzer, _pwmChannel);
        #endif
    }
    
    // Configura pino do LED
    if (_pinLed >= 0) {
        pinMode(_pinLed, OUTPUT);
        digitalWrite(_pinLed, LOW);
        _ledState = false;
    }
    
    // Configura pino do relé
    if (_pinRelay >= 0) {
        pinMode(_pinRelay, OUTPUT);
        digitalWrite(_pinRelay, LOW);
        _relayState = false;
    }
}

// ========== MÉTODOS DE ALERTA ==========

void BuzzerLed::alertaBuzzerLed(int times, int frequency, int duration) {
    for (int i = 0; i < times; i++) {
        ledOn();
        playTone(frequency, duration);
        delay(duration);
        ledOff();
        stopTone();
        
        // Pausa entre alertas (exceto no último)
        if (i < times - 1) {
            delay(duration);
        }
    }
}

void BuzzerLed::turnOff() {
    ledOff();
    stopTone();
}

// ========== MÉTODOS DO BUZZER ==========

void BuzzerLed::playTone(unsigned int frequency, unsigned long duration) {
    if (_pinBuzzer < 0 || frequency == 0) return;
    
    toneInternal(frequency);
    
    if (duration > 0) {
        delay(duration);
        noToneInternal();
    }
}

void BuzzerLed::stopTone() {
    noToneInternal();
}

void BuzzerLed::toneInternal(unsigned int frequency) {
    #ifdef ESP32
    ledcWriteTone(_pwmChannel, frequency);
    #else
    tone(_pinBuzzer, frequency);
    #endif
}

void BuzzerLed::noToneInternal() {
    #ifdef ESP32
    ledcWriteTone(_pwmChannel, 0);
    #else
    noTone(_pinBuzzer);
    #endif
}

void BuzzerLed::playStartupTune() {
    // Melodia simples de startup (escala ascendente)
    int melody[] = {NOTE_C4, NOTE_E4, NOTE_G4, NOTE_C5};
    int durations[] = {150, 150, 150, 300};
    
    for (int i = 0; i < 4; i++) {
        playTone(melody[i], durations[i]);
        delay(50);
    }
}

void BuzzerLed::playMarioTune() {
    // Tema do Super Mario Bros (simplificado)
    int melody[] = {
        NOTE_E5, NOTE_E5, REST, NOTE_E5, REST, NOTE_C5, NOTE_E5, REST,
        NOTE_G5, REST, REST, REST, NOTE_G4, REST, REST, REST
    };
    int durations[] = {
        150, 150, 150, 150, 150, 150, 150, 150,
        150, 150, 150, 150, 150, 150, 150, 150
    };
    
    for (int i = 0; i < 16; i++) {
        if (melody[i] == REST) {
            delay(durations[i]);
        } else {
            playTone(melody[i], durations[i]);
            delay(50);
        }
    }
}

void BuzzerLed::playStarWarsTune() {
    // Tema de Star Wars (Imperial March - simplificado)
    int melody[] = {
        NOTE_A4, NOTE_A4, NOTE_A4, NOTE_F4, NOTE_C5,
        NOTE_A4, NOTE_F4, NOTE_C5, NOTE_A4
    };
    int durations[] = {
        500, 500, 500, 350, 150,
        500, 350, 150, 650
    };
    
    for (int i = 0; i < 9; i++) {
        playTone(melody[i], durations[i]);
        delay(50);
    }
}

void BuzzerLed::playHappyBirthday() {
    // Happy Birthday
    int melody[] = {
        NOTE_C4, NOTE_C4, NOTE_D4, NOTE_C4, NOTE_F4, NOTE_E4,
        NOTE_C4, NOTE_C4, NOTE_D4, NOTE_C4, NOTE_G4, NOTE_F4,
        NOTE_C4, NOTE_C4, NOTE_C5, NOTE_A4, NOTE_F4, NOTE_E4, NOTE_D4,
        NOTE_AS4, NOTE_AS4, NOTE_A4, NOTE_F4, NOTE_G4, NOTE_F4
    };
    int durations[] = {
        200, 200, 400, 400, 400, 800,
        200, 200, 400, 400, 400, 800,
        200, 200, 400, 400, 400, 400, 400,
        200, 200, 400, 400, 400, 800
    };
    
    for (int i = 0; i < 25; i++) {
        playTone(melody[i], durations[i]);
        delay(50);
    }
}

void BuzzerLed::beep() {
    playTone(1000, 100);
    delay(50);
}

void BuzzerLed::doubleBeep() {
    beep();
    delay(100);
    beep();
}

void BuzzerLed::siren(unsigned long duration) {
    unsigned long startTime = millis();
    bool highTone = true;
    
    while (millis() - startTime < duration) {
        if (highTone) {
            playTone(800, 200);
        } else {
            playTone(400, 200);
        }
        highTone = !highTone;
    }
    stopTone();
}

// ========== MÉTODOS DO LED ==========

void BuzzerLed::ledOn() {
    if (_pinLed < 0) return;
    digitalWrite(_pinLed, HIGH);
    _ledState = true;
}

void BuzzerLed::ledOff() {
    if (_pinLed < 0) return;
    digitalWrite(_pinLed, LOW);
    _ledState = false;
}

void BuzzerLed::ledToggle() {
    if (_pinLed < 0) return;
    _ledState = !_ledState;
    digitalWrite(_pinLed, _ledState ? HIGH : LOW);
}

void BuzzerLed::ledBlink(int times, unsigned long onMs, unsigned long offMs) {
    for (int i = 0; i < times; i++) {
        ledOn();
        delay(onMs);
        ledOff();
        if (i < times - 1) {
            delay(offMs);
        }
    }
}

void BuzzerLed::ledPulse(int cycles, unsigned long duration) {
    if (_pinLed < 0) return;
    
    // Verifica se o pino suporta PWM
    if (!isPwmPin(_pinLed)) {
        // Fallback para blink se não suportar PWM
        ledBlink(cycles * 2, duration / 4, duration / 4);
        return;
    }
    
    for (int cycle = 0; cycle < cycles; cycle++) {
        // Fade in
        for (int brightness = 0; brightness <= 255; brightness += 5) {
            ledSetBrightness(brightness);
            delay(duration / 100);
        }
        // Fade out
        for (int brightness = 255; brightness >= 0; brightness -= 5) {
            ledSetBrightness(brightness);
            delay(duration / 100);
        }
    }
    ledOff();
}

void BuzzerLed::ledBreathe(int cycles) {
    ledPulse(cycles, 2000);
}

void BuzzerLed::ledSetBrightness(uint8_t brightness) {
    if (_pinLed < 0) return;
    
    #ifdef ESP32
    // Usa PWM no ESP32
    if (!_ledPwmConfigured) {
        ledcSetup(_ledPwmChannel, 5000, 8); // 5kHz, 8 bits
        ledcAttachPin(_pinLed, _ledPwmChannel);
        _ledPwmConfigured = true;
    }
    
    ledcWrite(_ledPwmChannel, brightness);
    _ledState = (brightness > 0);
    #else
    // Usa analogWrite em outras plataformas
    analogWrite(_pinLed, brightness);
    _ledState = (brightness > 0);
    #endif
}

void BuzzerLed::ledSOS() {
    // S: 3 curtos
    ledBlink(3, 150, 150);
    delay(300);
    
    // O: 3 longos
    ledBlink(3, 500, 150);
    delay(300);
    
    // S: 3 curtos
    ledBlink(3, 150, 150);
}

void BuzzerLed::ledHeartbeat(int times) {
    for (int i = 0; i < times; i++) {
        // Primeiro batimento
        ledOn();
        delay(100);
        ledOff();
        delay(100);
        
        // Segundo batimento
        ledOn();
        delay(100);
        ledOff();
        delay(600); // Pausa entre batimentos
    }
}

// ========== MÉTODOS DO RELÉ ==========

void BuzzerLed::relayOn() {
    if (_pinRelay < 0) return;
    digitalWrite(_pinRelay, HIGH);
    _relayState = true;
}

void BuzzerLed::relayOff() {
    if (_pinRelay < 0) return;
    digitalWrite(_pinRelay, LOW);
    _relayState = false;
}

void BuzzerLed::relayToggle() {
    if (_pinRelay < 0) return;
    _relayState = !_relayState;
    digitalWrite(_pinRelay, _relayState ? HIGH : LOW);
}

bool BuzzerLed::relayState() const {
    return _relayState;
}

void BuzzerLed::relayPulse(unsigned long onMs) {
    relayOn();
    delay(onMs);
    relayOff();
}

// ========== MÉTODOS COMBINADOS ==========

void BuzzerLed::celebrate() {
    // Efeito de celebração com LED, buzzer e relé
    for (int i = 0; i < 3; i++) {
        ledOn();
        relayOn();
        playTone(NOTE_C5, 150);
        delay(150);
        
        ledOff();
        relayOff();
        playTone(NOTE_E5, 150);
        delay(150);
        
        ledOn();
        relayOn();
        playTone(NOTE_G5, 150);
        delay(150);
        
        ledOff();
        relayOff();
        delay(100);
    }
    
    // Final com acorde
    ledOn();
    relayOn();
    playTone(NOTE_C6, 500);
    delay(500);
    
    ledOff();
    relayOff();
    stopTone();
}

void BuzzerLed::criticalAlert() {
    // Alerta crítico intenso
    for (int i = 0; i < 5; i++) {
        ledOn();
        playTone(1500, 100);
        delay(100);
        
        ledOff();
        playTone(800, 100);
        delay(100);
    }
    ledOff();
    stopTone();
}

void BuzzerLed::successEffect() {
    // Efeito de sucesso melodioso
    int melody[] = {NOTE_G4, NOTE_C5, NOTE_E5, NOTE_G5};
    int durations[] = {100, 100, 100, 300};
    
    for (int i = 0; i < 4; i++) {
        ledOn();
        playTone(melody[i], durations[i]);
        delay(durations[i] + 20);
        ledOff();
    }
}

// ========== MÉTODOS PRIVADOS ==========

bool BuzzerLed::isPwmPin(int pin) const {
    #ifdef ESP32
    // No ESP32, a maioria dos pinos GPIO podem ser PWM
    // Exceções: pinos somente-leitura (ex: 34-39 no ESP32 padrão)
    // Pinos 34-39 são ADC1 e não suportam PWM
    if (pin >= 34 && pin <= 39) return false;
    return (pin >= 0);
    #else
    // Para Arduino, verifica pinos PWM comuns
    const int pwmPins[] = {3, 5, 6, 9, 10, 11};
    for (int i = 0; i < 6; i++) {
        if (pin == pwmPins[i]) return true;
    }
    return false;
    #endif
}
