// //Verifica a vibração máxima permitida com base no valor da variável "LIMIAR_VIBRACAO", caso ultrapasse esse limiar envia um alerta
// //

// #include <Arduino.h>
// #include <Wire.h>
// #include <MPU6050.h>
// #include <HTTPClient.h>
// #include <ArduinoJson.h>
// #include "config.h"
// #include "display_manager.h"

// // === CONFIGURAÇÃO DE REDE E API ===
// const char* ssid = NETWORK_SSID;
// const char* password = NETWORK_PASSWORD;
// const int canal_wifi = 6; // Canal do WiFi (no uso real, deixar automático)
// const char* endpoint_api = API_URL; // URL da API
// const String init_sensor = String(endpoint_api) + "/init/";     // Endpoint de inicialização
// const String post_sensor = String(endpoint_api) + "/leitura/";  // Endpoint de envio de dados

// // === FUNÇÃO DE CONEXÃO WI-FI ===
// void conectaWiFi() {
//   WiFi.begin(ssid, password, canal_wifi);
//   displayPrint("Conectando ao WiFi");
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   displayPrint("WiFi conectado!");
// }

// // === FUNÇÃO DE ENVIO DE DADOS PARA API ===
// int post_data(JsonDocument& doc, const String& endpoint_api) {
//   Serial.println("Enviando dados para a API: " + endpoint_api);

//   if (WiFi.status() == WL_CONNECTED) {
//     HTTPClient http;
//     http.begin(endpoint_api);

//     String jsonStr;
//     serializeJson(doc, jsonStr);
//     int httpCode = http.POST(jsonStr);

//     if (httpCode > 0) {
//       Serial.println("Status code: " + String(httpCode));
//       String payload = http.getString();
//       Serial.println(payload);
//     } else {
//       Serial.println("Erro na requisição");
//     }
//     http.end();
//     return httpCode;
//   } else {
//     Serial.println("WiFi desconectado, impossível fazer requisição!");
//   }

//   return -1; // Retorna -1 se não conseguiu enviar os dados

// }

// // === IDENTIFICAÇÃO DO DISPOSITIVO ===
// char chipidStr[17];
// bool iniciou_sensor = false;

// void iniciar_sensor() {
//   uint64_t chipid = ESP.getEfuseMac();
//   sprintf(chipidStr, "%016llX", chipid);
  
//   // Exibe informações de inicialização
//   char buffer[64];
//   snprintf(buffer, sizeof(buffer), "Chip ID: %s", chipidStr);
//   displayPrint(buffer);
//   delay(1000);
  
//   snprintf(buffer, sizeof(buffer), "URL: %s", endpoint_api);
//   displayPrint(buffer);
//   delay(1000);

//   JsonDocument doc;
//   doc["serial"] = chipidStr; // Adiciona o Chip ID ao JSON
//   int httpcode = post_data(doc, init_sensor); // Envia o Chip ID para a API

//   if (httpcode >= 200 && httpcode < 300) {
//     displayPrint("Sensor iniciado com sucesso!");
//     delay(1000); // delay para garantir que a mensagem seja visível
//     iniciou_sensor = true;
//   } else {
//     snprintf(buffer, sizeof(buffer), "Falha ao iniciar: %d", httpcode);
//     displayPrint(buffer);
//     delay(1000); // delay para garantir que a mensagem seja visível
//   }
// }

// MPU6050 mpu;

// // Pinos do LDR, Relé, LED e Buzzer
// const int LDR_PIN = 34;      // Pino do LDR
// const int RELAY_PIN = 32;    // Pino do Relé
// const int LED_PIN = 15;      // Pino do LED
// const int BUZZER_PIN = 2;    // Pino do Buzzer

// // Variáveis
// float vibracaoTotal = 0;
// float vibracaoMedia = 0;
// const int NUM_AMOSTRAS = 100;
// const float LIMIAR_VIBRACAO = 1.0;  // Ajuste esse valor com base nos testes


// void setup() {
//   Serial.begin(115200);
  
//   pinMode(RELAY_PIN, OUTPUT);
//   pinMode(LED_PIN, OUTPUT);
//   pinMode(BUZZER_PIN, OUTPUT);
//   // Configuração do PWM para o buzzer
//   ledcSetup(0, 2000, 8); // Canal 0, 2kHz, 8 bits
//   ledcAttachPin(BUZZER_PIN, 0);

//   // Inicializa o I2C e o MPU6050
//   Wire.begin(21, 22);  // SDA: 21, SCL: 22 para ESP32

//   // Inicializa o display manager (LCD + Serial)
//   displayInit();
//   delay(1000);

//   mpu.initialize();
//   while (!mpu.testConnection()) {
//     displayPrint("MPU6050 nao conectado!");
//     delay(1000);
//   }

//   conectaWiFi();

// }

// void loop() {

//   if (!iniciou_sensor) {
//     iniciar_sensor();
//   }

//   JsonDocument doc;
//   doc["serial"] = chipidStr; // Adiciona o Chip ID ao JSON

//   // Lê o valor do LDR
//   int ldrValue = analogRead(LDR_PIN);
//   int lux = map(ldrValue, 0, 4095, 0, 2000); 
//   doc["lux"] = lux; // Adiciona o valor de luminosidade ao JSON

//   // Lê a temperatura do MPU6050
//   int rawTemp = mpu.getTemperature();
//   float tempC = rawTemp / 340.0 + 36.53;  //Converte o valor bruto para graus Celsius
//   doc["temperatura"] = tempC; // Adiciona a temperatura ao JSON
  
//   // Prepara informações para exibição
//   char buffer[32];
  
//   // Limpa o display para nova leitura
//   displayClear();
  
//   // Linha 0: Temperatura
//   snprintf(buffer, sizeof(buffer), "Temp: %.1f C", tempC);
//   displayPrintAt(0, 0, buffer);

//   // Linha 1: Condição de luminosidade
//   // Adiciona informação extra de Lux ao Serial (não mostrado no LCD por falta de espaço)
//   if (lux < 500) {
//     displayPrintAt(0, 1, "Condicao: Escuro");
//     Serial.print(F(" (Lux: "));
//     Serial.print(lux);
//     Serial.print(F(") |"));
//     digitalWrite(LED_PIN, LOW);
//     digitalWrite(RELAY_PIN, LOW);
//     noTone(BUZZER_PIN);
//   } else {
//     displayPrintAt(0, 1, "Condicao: Claro");
//     Serial.print(F(" (Lux: "));
//     Serial.print(lux);
//     Serial.print(F(") |"));
//     for (int i = 0; i < 3; i++) { // Buzzer e LED piscam juntos por 3x
//       digitalWrite(LED_PIN, HIGH);
//       digitalWrite(RELAY_PIN, HIGH);
//       tone(BUZZER_PIN, 1000);
//       delay(300);
//       digitalWrite(LED_PIN, LOW);
//       digitalWrite(RELAY_PIN, LOW);
//       noTone(BUZZER_PIN);
//       delay(300);
//     }
//   }
//   delay(1000);

//   // Lê os valores brutos de aceleração
//   int16_t ax_raw, ay_raw, az_raw;
//   mpu.getAcceleration(&ax_raw, &ay_raw, &az_raw);

//   // Converte para g (gravidade da Terra)
//   float ax = ax_raw / 16384.0;
//   float ay = ay_raw / 16384.0;
//   float az = az_raw / 16384.0;
//   doc["acelerometro_x"] = ax; // Adiciona o valor de aceleração X ao JSON
//   doc["acelerometro_y"] = ay; // Adiciona o valor de aceleração Y ao JSON
//   doc["acelerometro_z"] = az; // Adiciona o valor de aceleração Z ao JSON

//   // Lê os valores brutos de rotação
//   int16_t gx_raw, gy_raw, gz_raw;
//   mpu.getRotation(&gx_raw, &gy_raw, &gz_raw);

//   // Converte para graus/segundo
//   float gx = gx_raw / 131.0;
//   float gy = gy_raw / 131.0;
//   float gz = gz_raw / 131.0;

//   // ### Calcula o nível de vibração ###
//   float somaVibracao = 0;

//   for (int i = 0; i < NUM_AMOSTRAS; i++) {

//     // Calcular o módulo da aceleração total
//     float modulo = sqrt(ax * ax + ay * ay + az * az);

//     // Subtrair 1g da gravidade estática
//     float vibracao = abs(modulo - 1.0);
//     somaVibracao += vibracao;

//     delay(5); // pequeno intervalo para capturar vibrações rápidas
//   }

//   vibracaoMedia = somaVibracao / NUM_AMOSTRAS;
//   doc["vibracao_media"] = vibracaoMedia; // Adiciona a vibração média ao JSON

//   // Informação adicional no Serial com mais precisão (2 decimais vs LCD que pode mostrar menos)
//   Serial.print(F(" Vibracao media: "));
//   Serial.print(vibracaoMedia, 2);
//   Serial.print(F(" |"));

//   displayClear();
//   snprintf(buffer, sizeof(buffer), "Vibracao: %.2f", vibracaoMedia);
//   displayPrintAt(0, 0, buffer);

//   if (vibracaoMedia > LIMIAR_VIBRACAO) {
//     displayPrintAt(0, 1, "#ALERTA DE VIBRACAO#");

//     for (int i = 0; i < 3; i++) { // Buzzer e LED piscam juntos por 3x
//       digitalWrite(LED_PIN, HIGH);
//       digitalWrite(RELAY_PIN, HIGH);
//       tone(BUZZER_PIN, 1000);
//       delay(300);
//       digitalWrite(LED_PIN, LOW);
//       digitalWrite(RELAY_PIN, LOW);
//       noTone(BUZZER_PIN);
//       delay(300);
//     }
  
//   } else {
//     displayPrintAt(0, 1, "Vibracao normal!");
//   }

//   // Alerta de temperatura
//   if (tempC > 70.0) {
//     displayPrintAt(0, 1, "#ALERTA: >70 C#");

//     for (int i = 0; i < 3; i++) {
//       digitalWrite(LED_PIN, HIGH);
//       digitalWrite(RELAY_PIN, HIGH);
//       tone(BUZZER_PIN, 1500);
//       delay(300);
//       digitalWrite(LED_PIN, LOW);
//       digitalWrite(RELAY_PIN, LOW);
//       noTone(BUZZER_PIN);
//       delay(300);
//     }
//   }

//   // Exibe os valores de aceleração X, Y, Z no LCD e Monitor Serial
//   displayPrintAt(0, 2, "Accelerometer:");
  
//   snprintf(buffer, sizeof(buffer), "x:%.1f y:%.1f z:%.1f", ax, ay, az);
//   displayPrintAt(0, 3, buffer);

//   // Dados adicionais no Serial com mais precisão (2 decimais)
//   Serial.print(F(" X:"));
//   Serial.print(ax, 2);
//   Serial.print(F(" Y:"));
//   Serial.print(ay, 2);
//   Serial.print(F(" Z:"));
//   Serial.println(az, 2);

//   if (iniciou_sensor) {
//     // Envia os dados para a API
//     int httpcode = post_data(doc, post_sensor);
//     if (httpcode >= 200 && httpcode < 300) {
//       Serial.println(F("Dados enviados com sucesso!"));
//     } else {
//       Serial.println(F("Falha ao enviar dados."));
//     }
//   }

//   delay(5000);
// }
