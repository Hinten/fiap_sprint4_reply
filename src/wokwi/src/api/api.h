#ifndef API_H
#define API_H

#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "../conexao_wifi/conexao_wifi.h"
#include "../painel_lcd/painel_lcd.h"

struct Response {
    const int status_code;
    const String body;

    JsonDocument toJson() const {
        JsonDocument doc;
        const DeserializationError error = deserializeJson(doc, body);
        if (error) {
            return JsonDocument(nullptr);
        }
        return doc;
    }
};

class Api {
    String baseUrl;
    String initUrl;
    String leituraUrl;
    String chipIdStr;
    ConexaoWifi* conexao;
    PainelLCD* painel;

public:
    Api(const String& baseUrl, const String& initUrl, const String& leituraUrl, 
        ConexaoWifi* conexao, PainelLCD* painel = nullptr, const String& chipIdStr = "")
        : baseUrl(baseUrl), initUrl(initUrl), leituraUrl(leituraUrl), 
          chipIdStr(chipIdStr), conexao(conexao), painel(painel) {
        
        if (chipIdStr.isEmpty()) {
            uint64_t chipid = ESP.getEfuseMac();
            char buffer[17];
            sprintf(buffer, "%016llX", chipid);
            this->chipIdStr = String(buffer);
        }
    }

    Response get(const String& path) {
        if (!conexao->estaConectado()) {
            return {-1, "Not connected to WiFi"};
        }

        String url = baseUrl;
        if (!path.startsWith("/")) {
            url += "/";
        }
        url += path;

        HTTPClient http;
        http.begin(url);

        const int httpCode = http.GET();

        if (httpCode > 0) {
            const String payload = http.getString();
            http.end();
            return {httpCode, payload};
        } else {
            http.end();
            return {httpCode, "Request failed"};
        }
    }

    Response post(const String& path, const String& body, const String& contentType) {
        if (!conexao->estaConectado()) {
            return {-1, "Not connected to WiFi"};
        }

        String url = baseUrl;
        if (!path.startsWith("/")) {
            url += "/";
        }
        url += path;

        HTTPClient http;
        http.begin(url);
        http.addHeader("Content-Type", contentType);

        const int httpCode = http.POST(body);

        if (httpCode > 0) {
            const String payload = http.getString();
            http.end();
            return {httpCode, payload};
        } else {
            http.end();
            return {httpCode, "Request failed"};
        }
    }

    Response post_json(const String& path, const JsonDocument& json) {
        String jsonStr;
        serializeJson(json, jsonStr);
        return post(path, jsonStr, "application/json");
    }

    Response post_init() {
        JsonDocument doc;
        doc["serial"] = chipIdStr;
        return post_json(initUrl, doc);
    }

    Response post_leitura(JsonDocument& json) {
        json["serial"] = chipIdStr;
        return post_json(leituraUrl, json);
    }

    String getChipId() const {
        return chipIdStr;
    }
};

#endif // API_H
