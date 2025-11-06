// /**
//  * Exemplo de uso da classe BuzzerLed
//  * 
//  * Este exemplo demonstra as funcionalidades principais da classe BuzzerLed,
//  * incluindo controle de buzzer, LED e relé.
//  */

// #include <Arduino.h>
// #include "buzzer.h"

// // Pinos (conforme config.h)
// const int BUZZER_PIN = 25;
// const int LED_PIN = 15;
// const int RELAY_PIN = 32;

// // Instância da classe
// BuzzerLed buzzer(BUZZER_PIN, LED_PIN, RELAY_PIN);

// void setup() {
//     Serial.begin(115200);
//     delay(100);
    
//     Serial.println("\n=== BuzzerLed Example ===");
    
//     // Inicializa os pinos
//     buzzer.setup();
//     delay(500);
    
//     // DEMO 1: Melodia de startup
//     Serial.println("\n1. Tocando melodia de startup...");
//     buzzer.playStartupTune();
//     delay(1000);
    
//     // DEMO 2: Efeitos de LED
//     Serial.println("2. Demonstrando efeitos de LED...");
    
//     Serial.println("   - Piscar 5 vezes");
//     buzzer.ledBlink(5, 100, 100);
//     delay(500);
    
//     Serial.println("   - Efeito de pulso");
//     buzzer.ledPulse(2, 1000);
//     delay(500);
    
//     Serial.println("   - SOS");
//     buzzer.ledSOS();
//     delay(1000);
    
//     Serial.println("   - Heartbeat");
//     buzzer.ledHeartbeat(3);
//     delay(1000);
    
//     // DEMO 3: Tons e beeps
//     Serial.println("3. Demonstrando tons...");
    
//     Serial.println("   - Beep simples");
//     buzzer.beep();
//     delay(500);
    
//     Serial.println("   - Beep duplo");
//     buzzer.doubleBeep();
//     delay(500);
    
//     Serial.println("   - Sirene");
//     buzzer.siren(2000);
//     delay(500);
    
//     // DEMO 4: Melodias
//     Serial.println("4. Tocando melodias...");
    
//     Serial.println("   - Super Mario");
//     buzzer.playMarioTune();
//     delay(1000);
    
//     Serial.println("   - Star Wars");
//     buzzer.playStarWarsTune();
//     delay(1000);
    
//     // DEMO 5: Controle de relé
//     Serial.println("5. Demonstrando controle de relé...");
    
//     Serial.println("   - Ligar relé");
//     buzzer.relayOn();
//     delay(1000);
    
//     Serial.println("   - Desligar relé");
//     buzzer.relayOff();
//     delay(1000);
    
//     Serial.println("   - Toggle relé (3x)");
//     for (int i = 0; i < 3; i++) {
//         buzzer.relayToggle();
//         Serial.print("      Estado: ");
//         Serial.println(buzzer.relayState() ? "ON" : "OFF");
//         delay(500);
//     }
//     delay(1000);
    
//     // DEMO 6: Efeitos combinados
//     Serial.println("6. Demonstrando efeitos combinados...");
    
//     Serial.println("   - Alerta crítico");
//     buzzer.criticalAlert();
//     delay(1000);
    
//     Serial.println("   - Efeito de sucesso");
//     buzzer.successEffect();
//     delay(1000);
    
//     Serial.println("   - Celebração");
//     buzzer.celebrate();
//     delay(1000);
    
//     // DEMO 7: Alerta combinado (como usado no sketch.cpp)
//     Serial.println("7. Alerta combinado (buzzer + LED)...");
//     buzzer.alertaBuzzerLed(3, 1000, 300);
//     delay(1000);
    
//     Serial.println("\n=== Demo completo! ===");
//     Serial.println("Entrando no loop...\n");
// }

// void loop() {
//     // Exemplo de loop: alterna LED e relé a cada 5 segundos
//     static unsigned long lastToggle = 0;
//     static int state = 0;
    
//     unsigned long now = millis();
    
//     if (now - lastToggle >= 5000) {
//         lastToggle = now;
        
//         switch (state) {
//             case 0:
//                 Serial.println("Loop: LED piscando...");
//                 buzzer.ledBlink(3, 200, 200);
//                 break;
                
//             case 1:
//                 Serial.println("Loop: Beep duplo...");
//                 buzzer.doubleBeep();
//                 break;
                
//             case 2:
//                 Serial.println("Loop: Toggle relé...");
//                 buzzer.relayToggle();
//                 Serial.print("Estado do relé: ");
//                 Serial.println(buzzer.relayState() ? "ON" : "OFF");
//                 break;
                
//             case 3:
//                 Serial.println("Loop: Efeito de sucesso...");
//                 buzzer.successEffect();
//                 break;
//         }
        
//         state = (state + 1) % 4;
//     }
    
//     // Pequeno delay para não sobrecarregar
//     delay(100);
// }

// /**
//  * EXEMPLO DE USO EM CENÁRIOS REAIS
//  */

// // Exemplo 1: Alerta de temperatura
// void alertaTemperatura(float temperatura) {
//     if (temperatura > 70.0) {
//         Serial.println("ALERTA: Temperatura alta!");
//         buzzer.alertaBuzzerLed(3, 1500, 300);
//     } else if (temperatura > 50.0) {
//         Serial.println("Aviso: Temperatura elevada");
//         buzzer.beep();
//         buzzer.ledBlink(2, 200, 200);
//     }
// }

// // Exemplo 2: Indicação de status WiFi
// void statusWiFi(bool conectado) {
//     if (conectado) {
//         Serial.println("WiFi conectado!");
//         buzzer.successEffect();
//     } else {
//         Serial.println("WiFi desconectado!");
//         buzzer.alertaBuzzerLed(2, 2000, 500);
//     }
// }

// // Exemplo 3: Alerta de vibração
// void alertaVibracao(float nivelVibracao, float limiar) {
//     if (nivelVibracao > limiar) {
//         Serial.println("ALERTA: Vibração excessiva!");
//         buzzer.criticalAlert();
//         buzzer.relayOn();  // Pode desligar equipamento
//     } else {
//         buzzer.relayOff();
//     }
// }

// // Exemplo 4: Notificação de sucesso
// void notificarSucesso() {
//     buzzer.celebrate();
// }

// // Exemplo 5: Padrão de inicialização customizado
// void startupCustomizado() {
//     buzzer.setup();
    
//     // Pisca LED 3 vezes
//     buzzer.ledBlink(3, 100, 100);
//     delay(500);
    
//     // Toca melodia
//     buzzer.playStartupTune();
//     delay(500);
    
//     // Testa relé
//     buzzer.relayPulse(500);
//     delay(500);
    
//     // Efeito final
//     buzzer.successEffect();
// }
