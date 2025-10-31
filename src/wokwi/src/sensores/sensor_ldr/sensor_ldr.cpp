#include "sensor_ldr.h"
#include <math.h>

void SensorLDR::setup() {
    pinMode(ldrPin, INPUT);
    Serial.println(F("Sensor LDR initialized"));
}

int SensorLDR::readRaw() {
    return analogRead(ldrPin);
}

float SensorLDR::readLux() {
    const int adc = analogRead(ldrPin);
    
    if (adc == 0) {
        return NAN;
    }
    
    // Convert ADC to voltage
    const float vout = adc / 4095.0 * vcc;
    
    if (vout >= vcc || vout <= 0.0) {
        return NAN;
    }
    
    // Calculate LDR resistance
    const float rldr = ldrResistor * (vcc / vout - 1);
    
    // Estimate lux (approximate)
    const float lux = pow((luxCoefficient / rldr), (1.0 / gammaCoefficient));
    
    return lux;
}
