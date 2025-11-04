#ifndef MPU6050_SENSOR_H
#define MPU6050_SENSOR_H

#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>

class MPU6050Sensor {
    MPU6050 mpu;
    bool initialized;
    
    // Calibration offsets (optional)
    int16_t axOffset;
    int16_t ayOffset;
    int16_t azOffset;
    int16_t gxOffset;
    int16_t gyOffset;
    int16_t gzOffset;
    
    // Latest readings
    float ax, ay, az;  // Acceleration in g
    float gx, gy, gz;  // Gyroscope in degrees/second
    float temperature; // Temperature in Celsius
    
public:
    MPU6050Sensor()
        : initialized(false),
          axOffset(0), ayOffset(0), azOffset(0),
          gxOffset(0), gyOffset(0), gzOffset(0),
          ax(0), ay(0), az(0),
          gx(0), gy(0), gz(0),
          temperature(0) {}

    bool begin(TwoWire& wire = Wire);
    bool testConnection();
    void setDLPF(uint8_t mode);
    void calibrate(int samples = 1000);
    
    void readAcceleration();
    void readGyroscope();
    void readTemperature();
    void readAll();
    
    float calculateVibration(int numSamples = 100, int delayMs = 5);
    
    // Getters for latest readings
    float getAx() const { return ax; }
    float getAy() const { return ay; }
    float getAz() const { return az; }
    float getGx() const { return gx; }
    float getGy() const { return gy; }
    float getGz() const { return gz; }
    float getTemperature() const { return temperature; }
    
    bool isInitialized() const { return initialized; }
};

#endif // MPU6050_SENSOR_H
