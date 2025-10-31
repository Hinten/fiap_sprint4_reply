#ifndef SENSOR_LDR_H
#define SENSOR_LDR_H

#include <Arduino.h>

class SensorLDR {
    uint8_t ldrPin;
    float vcc;
    float ldrResistor;
    float luxCoefficient;
    float gammaCoefficient;

public:
    SensorLDR(uint8_t ldrPin, float vcc = 3.3, float ldrResistor = 10000.0,
              float luxCoefficient = 500000.0, float gammaCoefficient = 0.7)
        : ldrPin(ldrPin), vcc(vcc), ldrResistor(ldrResistor),
          luxCoefficient(luxCoefficient), gammaCoefficient(gammaCoefficient) {}

    void setup();
    float readLux();
    int readRaw();
};

#endif // SENSOR_LDR_H
