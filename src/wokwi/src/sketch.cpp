#include <Arduino.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include "config.h"
#include "painel_lcd/painel_lcd.h"
#include "conexao_wifi/conexao_wifi.h"
#include "api/api.h"
#include "sensores/sensor_ldr/sensor_ldr.h"
#include "sensores/mpu6050/MPU6050Sensor.h"
#include "buzzer/buzzer.h"

// ===== INSTÂNCIAS GLOBAIS =====
PainelLCD painel(LCD_I2C_ADDRESS, SELECTED_LCD, I2C_SDA_PIN, I2C_SCL_PIN);
ConexaoWifi conexaoWifi(NETWORK_SSID, NETWORK_PASSWORD, &painel, 10000);
Api api(API_BASE_URL, API_INIT_URL, API_LEITURA_URL, &conexaoWifi, &painel);
SensorLDR sensorLdr(LDR_PIN, LDR_VCC, LDR_RESISTOR);
MPU6050Sensor sensorMpu;
BuzzerLed buzzer(BUZZER_PIN, LED_PIN, RELAY_PIN);

// ===== VARIÁVEIS DE CONTROLE =====
struct SensorData {
    float temperature;
    float lux;
    float accelX;
    float accelY;
    float accelZ;
    float gyroX;
    float gyroY;
    float gyroZ;
    float vibration;
} sensorData;

struct NullableFloat {
    float value;
    bool isNull;

    // Construtor para valor definido
    NullableFloat(float val) : value(val), isNull(false) {}

    // Construtor para nulo
    NullableFloat() : value(0.0f), isNull(true) {}
};

struct SensorLimits {
    NullableFloat vibrationThresholdMin; // Limite de vibração para alerta
    NullableFloat vibrationThresholdMax;
    NullableFloat temperatureThresholdMin;
    NullableFloat temperatureThresholdMax;
    NullableFloat luxThresholdMin;
    NullableFloat luxThresholdMax;

    SensorLimits(NullableFloat vibrationMin, NullableFloat vibrationMax, NullableFloat temperatureMin, NullableFloat temperatureMax, NullableFloat luxMin, NullableFloat luxMax) :
    vibrationThresholdMin(vibrationMin),
    vibrationThresholdMax(vibrationMax),
    temperatureThresholdMin(temperatureMin),
    temperatureThresholdMax(temperatureMax),
    luxThresholdMin(luxMin),
    luxThresholdMax(luxMax) 
    {}
} sensorLimits(NullableFloat(), NullableFloat(1.0f), NullableFloat(), NullableFloat(70.0f), NullableFloat(500.0f), NullableFloat());

bool sensorIniciado = false;
unsigned long ultimoMillis = 0;

// ===== FUNÇÕES AUXILIARES =====

void iniciarSensor() {
    if (sensorIniciado) {
        return;
    }
    
    painel.printLCDSerial(0, 0, "Iniciando sensor...");
    
    if (!conexaoWifi.estaConectado()) {
        painel.printLCDSerial(0, 1, "WiFi desconectado");
        return;
    }
    
    Response response = api.post_init();

    if (response.status_code >= 200 && response.status_code < 300) {
        painel.printLCDSerial(0, 0, "Sensor iniciado!");
        Serial.println(F("Sensor iniciado com sucesso na API"));
        Serial.print(F("Chip ID: "));
        Serial.println(api.getChipId());
        sensorIniciado = true;

        JsonDocument doc = response.toJson();
        if (!doc.isNull()) {
            painel.printLCDSerial(0, 1, "Limiares Recebidos");
            SensorLimits newLimits(
                doc["vibration_threshold_min"].isNull() ? NullableFloat() : NullableFloat(float(doc["vibration_threshold_min"])),
                doc["vibration_threshold_max"].isNull() ? NullableFloat() : NullableFloat(float(doc["vibration_threshold_max"])),
                doc["temperature_threshold_min"].isNull() ? NullableFloat() : NullableFloat(float(doc["temperature_threshold_min"])),
                doc["temperature_threshold_max"].isNull() ? NullableFloat() : NullableFloat(float(doc["temperature_threshold_max"])),
                doc["lux_threshold_min"].isNull() ? NullableFloat() : NullableFloat(float(doc["lux_threshold_min"])),
                doc["lux_threshold_max"].isNull() ? NullableFloat() : NullableFloat(float(doc["lux_threshold_max"]))
            );

            sensorLimits = newLimits;
        }

        delay(1000);
    } else {
        char buffer[32];
        snprintf(buffer, sizeof(buffer), "Falha init: %d", response.status_code);
        painel.printLCDSerial(0, 0, buffer);
        Serial.print(F("Falha ao iniciar sensor. Status: "));
        Serial.println(response.status_code);
    }
}

bool hasSentData = false;
// ===== PRIMARY TASK - LEITURA DE SENSORES =====
void primaryTask() {
    // Lê temperatura do MPU6050
    sensorMpu.readTemperature();
    sensorData.temperature = sensorMpu.getTemperature();
    
    // Lê luminosidade do LDR
    sensorData.lux = sensorLdr.readLux();
    
    // Lê acelerômetro
    sensorMpu.readAcceleration();
    sensorData.accelX = sensorMpu.getAx();
    sensorData.accelY = sensorMpu.getAy();
    sensorData.accelZ = sensorMpu.getAz();
    
    // Lê giroscópio
    sensorMpu.readGyroscope();
    sensorData.gyroX = sensorMpu.getGx();
    sensorData.gyroY = sensorMpu.getGy();
    sensorData.gyroZ = sensorMpu.getGz();
    
    // Calcula vibração média
    sensorData.vibration = sensorMpu.calculateVibration(VIBRATION_SAMPLES, 5);
    
    // Exibe informações no display
    char buffer[32];
    painel.clear();
        
    // Linha 1: Luminosidade
    if (!sensorLimits.luxThresholdMin.isNull && sensorData.lux < sensorLimits.luxThresholdMin.value) {
        snprintf(buffer, sizeof(buffer), "Lux: %.0f (Escuro)", sensorData.lux);
        painel.printLCDSerial(0, 0, buffer);
        buzzer.alertaBuzzerLed(3, 1000, 300);
    } else if (!sensorLimits.luxThresholdMax.isNull && sensorData.lux > sensorLimits.luxThresholdMax.value) {
        snprintf(buffer, sizeof(buffer), "Lux: %.0f (Claro)", sensorData.lux);
        painel.printLCDSerial(0, 0, buffer);
        buzzer.alertaBuzzerLed(3, 1000, 300);
    } else {
        snprintf(buffer, sizeof(buffer), "Lux: %.0f", sensorData.lux);
        painel.printLCDSerial(0, 0, buffer);
    }
        
    snprintf(buffer, sizeof(buffer), "Vib: %.2f", sensorData.vibration);
    painel.printLCDSerial(0, 1, buffer);

    if (!sensorLimits.vibrationThresholdMax.isNull && sensorData.vibration > sensorLimits.vibrationThresholdMax.value) {
        painel.printLCDSerial(0, 1, "#ALERTA VIBRACAO#");
        buzzer.alertaBuzzerLed(3, 1200, 300);
    } else if (!sensorLimits.vibrationThresholdMin.isNull && sensorData.vibration < sensorLimits.vibrationThresholdMin.value) {
        painel.printLCDSerial(0, 1, "#ALERTA VIBRACAO#");
        buzzer.alertaBuzzerLed(3, 1200, 300);   
    } else {
        snprintf(buffer, sizeof(buffer), "Vib: %.2f", sensorData.vibration);
        painel.printLCDSerial(0, 1, buffer);
    }
    
    delay(1000);

    if (!sensorLimits.temperatureThresholdMax.isNull && sensorData.temperature > sensorLimits.temperatureThresholdMax.value) {
        painel.printLCDSerial(0, 2, "#ALERTA TEMP#");
        buzzer.alertaBuzzerLed(3, 1500, 300);
    } else if (!sensorLimits.temperatureThresholdMin.isNull && sensorData.temperature < sensorLimits.temperatureThresholdMin.value) {
        painel.printLCDSerial(0, 2, "#ALERTA TEMP#");
        buzzer.alertaBuzzerLed(3, 1500, 300);   
    } else {
        snprintf(buffer, sizeof(buffer), "Temp: %.2fC", sensorData.temperature);
        painel.printLCDSerial(0, 2, buffer);
    }

    delay(1000);

    painel.clear();
    
    painel.printLCDSerial(0, 2, "Accelerometer:");
    snprintf(buffer, sizeof(buffer), "x:%.1f y:%.1f z:%.1f", 
                sensorData.accelX, sensorData.accelY, sensorData.accelZ);
    painel.printLCDSerial(0, 3, buffer);
    
    delay(1000);

    // Log detalhado no Serial
    Serial.print(F("Temp: "));
    Serial.print(sensorData.temperature, 3);
    Serial.print(F(" | Lux: "));
    Serial.print(sensorData.lux, 0);
    Serial.print(F(" | Vib: "));
    Serial.print(sensorData.vibration, 3);
    Serial.print(F(" | Accel X:"));
    Serial.print(sensorData.accelX, 3);
    Serial.print(F(" Y:"));
    Serial.print(sensorData.accelY, 3);
    Serial.print(F(" Z:"));
    Serial.println(sensorData.accelZ, 3);

    hasSentData = false;
}

// ===== SECONDARY TASK - ENVIO DE DADOS =====
void secondaryTask() {

    if (hasSentData){
        return;
    }

    // Verifica conexão WiFi
    if (!conexaoWifi.estaConectado()) {
        buzzer.alertaBuzzerLed(2, 2000, 500);
        Serial.println(F("WiFi desconectado. Tentando reconectar..."));
        conexaoWifi.connect();
        return;
    }
    
    // Inicializa sensor se necessário
    if (!sensorIniciado) {
        iniciarSensor();
        return;
    }
    
    // Prepara JSON com dados dos sensores
    JsonDocument doc;
    doc["temperatura"] = sensorData.temperature;
    doc["lux"] = sensorData.lux;
    doc["acelerometro_x"] = sensorData.accelX;
    doc["acelerometro_y"] = sensorData.accelY;
    doc["acelerometro_z"] = sensorData.accelZ;
    doc["vibracao_media"] = sensorData.vibration;
    
    // Envia dados para API
    Response response = api.post_leitura(doc);
    
    if (response.status_code >= 200 && response.status_code < 300) {
        Serial.println(F("Dados enviados com sucesso!"));
        hasSentData = true;
    } else {
        Serial.print(F("Falha ao enviar dados. Status: "));
        Serial.println(response.status_code);
        // Se falhar repetidamente, pode tentar reinicializar o sensor
        if (response.status_code == -1) {
            sensorIniciado = false;
        }
    }
}

// ===== SETUP =====
void setup() {
    // Inicializa Serial
    Serial.begin(115200);
    delay(100);
    Serial.println(F("\n=== ESP32 Industrial Monitor ==="));
    Serial.println(F("Version 2.0 - Modular Architecture"));
    
    // Configura pinos de saída
    buzzer.setup();
    
    // Inicializa I2C
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
    
    // Inicializa painel LCD
    painel.setup();
    delay(500);
    
    // Inicializa MPU6050
    painel.printLCDSerial(0, 0, "Init MPU6050...");
    if (sensorMpu.begin(Wire)) {
        painel.printLCDSerial(0, 1, "MPU6050 OK!");
    } else {
        painel.printLCDSerial(0, 1, "MPU6050 FALHOU!");
        while (true) {
            delay(1000);
            buzzer.criticalAlert();
        }
    }
    delay(1000);
    
    // Inicializa LDR
    sensorLdr.setup();
    
    // Conecta WiFi
    painel.printLCDSerial(0, 0, "Conectando WiFi...");
    conexaoWifi.setup();
    
    Serial.println(F("\n=== Setup completo! ===\n"));
    delay(1000);
    buzzer.playStartupTune();  // Toca melodia de inicialização
}

// ===== LOOP =====
void loop() {
    unsigned long agora = millis();
    
    // Executa primaryTask a cada PRIMARY_TASK_INTERVAL
    if (agora - ultimoMillis >= PRIMARY_TASK_INTERVAL) {
        ultimoMillis = agora;
        primaryTask();
    } else {
        // Executa secondaryTask no tempo restante
        secondaryTask();
        delay(SECONDARY_TASK_DELAY);
    }
}
