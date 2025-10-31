#ifndef CONEXAO_WIFI_H
#define CONEXAO_WIFI_H

#include <Arduino.h>
#include <WiFi.h>

// Forward declaration to avoid circular dependency
class PainelLCD;

class ConexaoWifi {
    const char* ssid;
    const char* password;
    PainelLCD* painel;
    unsigned long tempoMaximoConexao;
    bool conectado;

    void print_serial_or_lcd(const String& msg);

public:
    ConexaoWifi(const char* ssid, const char* password, PainelLCD* painel = nullptr, 
                unsigned long tempoMaximoConexao = 10000)
        : ssid(ssid), password(password), painel(painel), 
          tempoMaximoConexao(tempoMaximoConexao), conectado(false) {}

    void setup();
    void connect();
    bool estaConectado();
};

#endif // CONEXAO_WIFI_H
