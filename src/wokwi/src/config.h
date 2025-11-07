#ifndef CONFIG_H
#define CONFIG_H

/**
 * Configuração do tipo de painel LCD
 * 
 * Escolha uma das opções abaixo:
 * - LCD_NONE: Nenhum LCD conectado (apenas saída Serial)
 * - LCD_16x2: Painel LCD 16 colunas x 2 linhas
 * - LCD_20x4: Painel LCD 20 colunas x 4 linhas (padrão)
 */
enum LcdType {
  LCD_NONE = 0,
  LCD_16x2 = 1,
  LCD_20x4 = 2
};

// ===== CONFIGURAÇÃO DO USUÁRIO =====
// Altere esta linha para escolher o tipo de LCD:
const LcdType SELECTED_LCD = LCD_16x2;

// Configurações do LCD I2C
const int LCD_I2C_ADDRESS = 0x27;

// Delay para paginação de conteúdo (quando necessário para LCD 16x2)
const int DISPLAY_PAGE_DELAY_MS = 2000;

// ===== CONFIGURAÇÃO DE REDE E API =====
#ifndef NETWORK_SSID
#define NETWORK_SSID "Wokwi-GUEST"
#endif

#ifndef NETWORK_PASSWORD
#define NETWORK_PASSWORD ""
#endif

#ifndef API_URL
#define API_URL "http://localhost:8180"
#endif

// API Endpoints
#define API_BASE_URL API_URL
#define API_INIT_URL "/init/"
#define API_LEITURA_URL "/leitura/"

// ===== CONFIGURAÇÃO DE PINOS =====
// I2C
const int I2C_SDA_PIN = 21;
const int I2C_SCL_PIN = 22;

// Sensores
const int LDR_PIN = 34;
const int MPU6050_INTERRUPT_PIN = 2;  // Opcional

// Atuadores
const int RELAY_PIN = 32;
const int LED_PIN = 15;
const int BUZZER_PIN = 25;

// Botões e controles
const int BUTTON_CANCEL_ALERT_PIN = 16;  // Botão para cancelar alerta sonoro
const int BUTTON_PIN = 16;   // novo botão

// ===== CONFIGURAÇÃO DE SENSORES =====
// LDR
const float LDR_VCC = 3.3;
const float LDR_RESISTOR = 10000.0;

// MPU6050
const int VIBRATION_SAMPLES = 100;      // Número de amostras para cálculo

// ===== CONFIGURAÇÃO DE TIMING =====
const unsigned long PRIMARY_TASK_INTERVAL = 10000;   // 5 segundos
const unsigned long SECONDARY_TASK_DELAY = 100;     // 100ms

#endif // CONFIG_H
