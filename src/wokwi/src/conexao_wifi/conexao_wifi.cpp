#include "conexao_wifi.h"
#include "../painel_lcd/painel_lcd.h"

void ConexaoWifi::print_serial_or_lcd(const String& msg) {
    if (painel != nullptr) {
        painel->printLCDSerial(0, 0, msg);
    } else {
        Serial.println(msg);
    }
}

void ConexaoWifi::connect() {
    WiFi.begin(ssid, password);
    print_serial_or_lcd("Conectando ao WiFi");
    
    const unsigned long inicio = millis();
    conectado = false;
    
    while (WiFi.status() != WL_CONNECTED && (millis() - inicio) < tempoMaximoConexao) {
        delay(500);
        Serial.print(".");
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        print_serial_or_lcd("WiFi conectado!");
        conectado = true;
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
    } else {
        print_serial_or_lcd("Falha ao conectar!");
        conectado = false;
    }
}

void ConexaoWifi::setup() {
    connect();
}

bool ConexaoWifi::estaConectado() {
    conectado = (WiFi.status() == WL_CONNECTED);
    return conectado;
}
