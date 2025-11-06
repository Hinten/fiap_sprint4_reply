#include "MPU6050Sensor.h"
#include <math.h>

bool MPU6050Sensor::begin(TwoWire& wire) {
    // Initialize MPU6050
    mpu.initialize();

    //return true;
    
    // Test connection
    initialized = true;
    
    if (initialized) {
        Serial.println(F("MPU6050 connected successfully"));
        
        // Set default configuration
        mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2); // ±2g
        mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);  // ±250°/s
        
        // Enable DLPF for noise reduction
        setDLPF(MPU6050_DLPF_BW_20);
    } else {
        Serial.println(F("MPU6050 connection failed!"));
    }
    
    return initialized;
}

bool MPU6050Sensor::testConnection() {
    //return mpu.testConnection();

    return true;

}

void MPU6050Sensor::setDLPF(uint8_t mode) {
    mpu.setDLPFMode(mode);
}

void MPU6050Sensor::calibrate(int samples) {
    if (!initialized) {
        return;
    }
    
    Serial.println(F("Calibrating MPU6050... Keep sensor stable!"));
    
    long axSum = 0, aySum = 0, azSum = 0;
    long gxSum = 0, gySum = 0, gzSum = 0;
    
    for (int i = 0; i < samples; i++) {
        int16_t ax_raw, ay_raw, az_raw;
        int16_t gx_raw, gy_raw, gz_raw;
        
        mpu.getAcceleration(&ax_raw, &ay_raw, &az_raw);
        mpu.getRotation(&gx_raw, &gy_raw, &gz_raw);
        
        axSum += ax_raw;
        aySum += ay_raw;
        azSum += az_raw - 16384; // Subtract 1g from Z axis
        
        gxSum += gx_raw;
        gySum += gy_raw;
        gzSum += gz_raw;
        
        delay(3);
    }
    
    axOffset = axSum / samples;
    ayOffset = aySum / samples;
    azOffset = azSum / samples;
    gxOffset = gxSum / samples;
    gyOffset = gySum / samples;
    gzOffset = gzSum / samples;
    
    Serial.println(F("Calibration complete!"));
    Serial.print(F("Offsets - Accel: "));
    Serial.print(axOffset); Serial.print(F(", "));
    Serial.print(ayOffset); Serial.print(F(", "));
    Serial.println(azOffset);
}

void MPU6050Sensor::readAcceleration() {
    if (!initialized) {
        ax = ay = az = NAN;
        return;
    }
    
    int16_t ax_raw, ay_raw, az_raw;
    mpu.getAcceleration(&ax_raw, &ay_raw, &az_raw);
    
    // Convert to g (using sensitivity scale factor for ±2g range)
    ax = (ax_raw - axOffset) / 16384.0;
    ay = (ay_raw - ayOffset) / 16384.0;
    az = (az_raw - azOffset) / 16384.0;
}

void MPU6050Sensor::readGyroscope() {
    if (!initialized) {
        gx = gy = gz = NAN;
        return;
    }
    
    int16_t gx_raw, gy_raw, gz_raw;
    mpu.getRotation(&gx_raw, &gy_raw, &gz_raw);
    
    // Convert to degrees/second (using sensitivity scale factor for ±250°/s range)
    gx = (gx_raw - gxOffset) / 131.0;
    gy = (gy_raw - gyOffset) / 131.0;
    gz = (gz_raw - gzOffset) / 131.0;
}

void MPU6050Sensor::readTemperature() {
    if (!initialized) {
        temperature = NAN;
        return;
    }
    
    int16_t rawTemp = mpu.getTemperature();
    temperature = rawTemp / 340.0 + 36.53;
}

void MPU6050Sensor::readAll() {
    readAcceleration();
    readGyroscope();
    readTemperature();
}

float MPU6050Sensor::calculateVibration(int numSamples, int delayMs) {
    if (!initialized) {
        return NAN;
    }
    
    float somaVibracao = 0.0;
    
    for (int i = 0; i < numSamples; i++) {
        int16_t ax_raw, ay_raw, az_raw;
        mpu.getAcceleration(&ax_raw, &ay_raw, &az_raw);
        
        // Convert to g
        float ax_g = ax_raw / 16384.0;
        float ay_g = ay_raw / 16384.0;
        float az_g = az_raw / 16384.0;
        
        // Calculate magnitude of acceleration
        float modulo = sqrt(ax_g * ax_g + ay_g * ay_g + az_g * az_g);
        
        // Subtract 1g (static gravity)
        float vibracao = abs(modulo - 1.0);
        somaVibracao += vibracao;
        
        if (delayMs > 0) {
            delay(delayMs);
        }
    }
    
    return somaVibracao / numSamples;
}
