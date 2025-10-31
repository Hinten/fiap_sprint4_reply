#ifndef BUZZER_H
#define BUZZER_H

#include <Arduino.h>

/**
 * @brief Classe para controlar Buzzer, LED e Relé
 * 
 * Esta classe gerencia três componentes:
 * - Buzzer: para alertas sonoros e melodias
 * - LED: para indicações visuais
 * - Relé: para controle de carga externa
 */
class BuzzerLed {
public:
    /**
     * @brief Construtor da classe BuzzerLed
     * @param pinBuzzer Pino do buzzer (padrão: 25)
     * @param pinLed Pino do LED (padrão: 15)
     * @param pinRelay Pino do relé (padrão: 32)
     */
    BuzzerLed(int pinBuzzer = 25, int pinLed = 15, int pinRelay = 32);

    /**
     * @brief Inicializa os pinos (deve ser chamado no setup())
     */
    void setup();

    // ========== MÉTODOS DE ALERTA ==========
    
    /**
     * @brief Alerta combinado de buzzer e LED
     * @param times Número de vezes para repetir o alerta
     * @param frequency Frequência do buzzer em Hz
     * @param duration Duração de cada ciclo em ms
     */
    void alertaBuzzerLed(int times, int frequency, int duration);

    /**
     * @brief Desliga buzzer e LED
     */
    void turnOff();

    // ========== MÉTODOS DO BUZZER ==========
    
    /**
     * @brief Toca uma nota específica
     * @param frequency Frequência em Hz
     * @param duration Duração em ms (0 = contínuo)
     */
    void playTone(unsigned int frequency, unsigned long duration = 0);

    /**
     * @brief Para o som do buzzer
     */
    void stopTone();

    /**
     * @brief Toca uma melodia simples de startup
     */
    void playStartupTune();

    /**
     * @brief Toca a melodia "Super Mario Bros"
     */
    void playMarioTune();

    /**
     * @brief Toca a melodia "Star Wars"
     */
    void playStarWarsTune();

    /**
     * @brief Toca a melodia "Happy Birthday"
     */
    void playHappyBirthday();

    /**
     * @brief Toca um beep curto
     */
    void beep();

    /**
     * @brief Toca dois beeps curtos
     */
    void doubleBeep();

    /**
     * @brief Sirene de alerta (tom alternado)
     * @param duration Duração total em ms
     */
    void siren(unsigned long duration = 2000);

    // ========== MÉTODOS DO LED ==========
    
    /**
     * @brief Liga o LED
     */
    void ledOn();

    /**
     * @brief Desliga o LED
     */
    void ledOff();

    /**
     * @brief Alterna o estado do LED
     */
    void ledToggle();

    /**
     * @brief Pisca o LED
     * @param times Número de piscadas
     * @param onMs Tempo ligado em ms (padrão: 200)
     * @param offMs Tempo desligado em ms (padrão: 200)
     */
    void ledBlink(int times = 1, unsigned long onMs = 200, unsigned long offMs = 200);

    /**
     * @brief Efeito de pulso no LED (fade in/out)
     * @param cycles Número de ciclos (padrão: 3)
     * @param duration Duração de cada ciclo em ms (padrão: 1000)
     */
    void ledPulse(int cycles = 3, unsigned long duration = 1000);

    /**
     * @brief Efeito de respiração (breathing) no LED
     * @param cycles Número de ciclos (padrão: 5)
     */
    void ledBreathe(int cycles = 5);

    /**
     * @brief Define o brilho do LED (requer pino PWM)
     * @param brightness Brilho de 0 a 255
     */
    void ledSetBrightness(uint8_t brightness);

    /**
     * @brief Pisca rápido (SOS em morse)
     */
    void ledSOS();

    /**
     * @brief Efeito de heartbeat (batimento cardíaco)
     * @param times Número de batimentos (padrão: 3)
     */
    void ledHeartbeat(int times = 3);

    // ========== MÉTODOS DO RELÉ ==========
    
    /**
     * @brief Liga o relé (ativa carga)
     */
    void relayOn();

    /**
     * @brief Desliga o relé (desativa carga)
     */
    void relayOff();

    /**
     * @brief Alterna o estado do relé
     */
    void relayToggle();

    /**
     * @brief Retorna o estado atual do relé
     * @return true se ligado, false se desligado
     */
    bool relayState() const;

    /**
     * @brief Pulsa o relé (liga e desliga)
     * @param onMs Tempo ligado em ms (padrão: 1000)
     */
    void relayPulse(unsigned long onMs = 1000);

    // ========== MÉTODOS COMBINADOS ==========
    
    /**
     * @brief Efeito de celebração (LED + Buzzer + Relé)
     */
    void celebrate();

    /**
     * @brief Efeito de alerta crítico (LED + Buzzer intenso)
     */
    void criticalAlert();

    /**
     * @brief Efeito de sucesso (LED + Buzzer melodioso)
     */
    void successEffect();

private:
    int _pinBuzzer;
    int _pinLed;
    int _pinRelay;
    bool _relayState;
    bool _ledState;
    
    // Canal PWM para o buzzer (ESP32)
    const int _pwmChannel = 0;
    const int _pwmResolution = 8;

    /**
     * @brief Verifica se o pino suporta PWM
     * @param pin Número do pino
     * @return true se suporta PWM
     */
    bool isPwmPin(int pin) const;

    /**
     * @brief Toca uma nota usando PWM (interno)
     * @param frequency Frequência em Hz
     */
    void toneInternal(unsigned int frequency);

    /**
     * @brief Para o tom (interno)
     */
    void noToneInternal();
};

// ========== DEFINIÇÕES DE NOTAS MUSICAIS ==========
// Frequências das notas em Hz
#define NOTE_B0  31
#define NOTE_C1  33
#define NOTE_CS1 35
#define NOTE_D1  37
#define NOTE_DS1 39
#define NOTE_E1  41
#define NOTE_F1  44
#define NOTE_FS1 46
#define NOTE_G1  49
#define NOTE_GS1 52
#define NOTE_A1  55
#define NOTE_AS1 58
#define NOTE_B1  62
#define NOTE_C2  65
#define NOTE_CS2 69
#define NOTE_D2  73
#define NOTE_DS2 78
#define NOTE_E2  82
#define NOTE_F2  87
#define NOTE_FS2 93
#define NOTE_G2  98
#define NOTE_GS2 104
#define NOTE_A2  110
#define NOTE_AS2 117
#define NOTE_B2  123
#define NOTE_C3  131
#define NOTE_CS3 139
#define NOTE_D3  147
#define NOTE_DS3 156
#define NOTE_E3  165
#define NOTE_F3  175
#define NOTE_FS3 185
#define NOTE_G3  196
#define NOTE_GS3 208
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_CS4 277
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_FS4 370
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_CS5 554
#define NOTE_D5  587
#define NOTE_DS5 622
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_FS5 740
#define NOTE_G5  784
#define NOTE_GS5 831
#define NOTE_A5  880
#define NOTE_AS5 932
#define NOTE_B5  988
#define NOTE_C6  1047
#define NOTE_CS6 1109
#define NOTE_D6  1175
#define NOTE_DS6 1245
#define NOTE_E6  1319
#define NOTE_F6  1397
#define NOTE_FS6 1480
#define NOTE_G6  1568
#define NOTE_GS6 1661
#define NOTE_A6  1760
#define NOTE_AS6 1865
#define NOTE_B6  1976
#define NOTE_C7  2093
#define NOTE_CS7 2217
#define NOTE_D7  2349
#define NOTE_DS7 2489
#define NOTE_E7  2637
#define NOTE_F7  2794
#define NOTE_FS7 2960
#define NOTE_G7  3136
#define NOTE_GS7 3322
#define NOTE_A7  3520
#define NOTE_AS7 3729
#define NOTE_B7  3951
#define NOTE_C8  4186
#define NOTE_CS8 4435
#define NOTE_D8  4699
#define NOTE_DS8 4978

#define REST 0

#endif // BUZZER_H
