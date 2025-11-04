#ifndef BUZZER_H
#define BUZZER_H

#include <Arduino.h>

class BuzzerLed {
    uint8_t buzzerPin;
    uint8_t ledPin;
    uint8_t relayPin;

public:
    BuzzerLed(int buzzer, int led, int relay) : buzzerPin(buzzer), ledPin(led), relayPin(relay) {
    }

    void playTone(int frequency, int duration) {
        tone(buzzerPin, frequency, duration);
    }

    void stopTone() {
        noTone(buzzerPin);
    }

    
    void alertaBuzzerLed(int repeticoes = 3, int frequencia = 1000, int duracao = 300) {
        for (int i = 0; i < repeticoes; i++) {
            digitalWrite(ledPin, HIGH);
            digitalWrite(relayPin, HIGH);
            tone(buzzerPin, frequencia);
            delay(duracao);
            digitalWrite(ledPin, LOW);
            digitalWrite(relayPin, LOW);
            noTone(buzzerPin);
            delay(duracao);
        }
    }

    void turnOff(){
        digitalWrite(ledPin, LOW);
        digitalWrite(relayPin, LOW);
        digitalWrite(buzzerPin, LOW);
    }

    void setup() {
        pinMode(buzzerPin, OUTPUT);
        pinMode(ledPin, OUTPUT);
        pinMode(relayPin, OUTPUT);
        
        // Configura PWM para buzzer
        ledcSetup(0, 2000, 8);
        ledcAttachPin(buzzerPin, 0);

        playTone(1000, 300);
        Serial.println(F("Buzzer ligado por 300ms"));
        // stopTone();
    }

};

#endif
