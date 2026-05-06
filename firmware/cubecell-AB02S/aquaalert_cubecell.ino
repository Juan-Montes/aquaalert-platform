/**
 * AquaAlert — CubeCell AB02S (HTCC-AB02S)
 * Sensor: JSN-SR04T → TRIG=GPIO1, ECHO=GPIO2
 * GPS:    deshabilitado (Fase 5)
 *
 * Payload Tipo A (4 bytes):
 *   [0-1] distance_mm  uint16 Big Endian
 *   [2-3] battery_mv   uint16 Big Endian
 */

#include "LoRaWan_APP.h"
#include "Arduino.h"

// ─── CREDENCIALES LORAWAN (OTAA) ────────────────────────────────────────────
uint8_t devEui[] = { 0xD0, 0x89, 0x05, 0xAA, 0xAC, 0xD7, 0x56, 0xFE };
uint8_t appEui[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
uint8_t appKey[] = { 0x98, 0xD9, 0x02, 0x75, 0x2D, 0x8C, 0x36, 0x04,
                     0x14, 0x50, 0xBB, 0xD5, 0x36, 0x55, 0x78, 0xDE };

// ─── ABP (requeridos por librería aunque usemos OTAA) ───────────────────────
uint8_t  nwkSKey[] = { 0x15,0xb1,0xd0,0xef,0xa4,0x63,0xdf,0xbe,
                       0x3d,0x11,0x18,0x1e,0x1e,0xc7,0xda,0x85 };
uint8_t  appSKey[] = { 0xd7,0x2c,0x78,0x75,0x8c,0xdc,0xca,0xbf,
                       0x55,0xee,0x4a,0x77,0x8d,0x16,0xef,0x67 };
uint32_t devAddr   = (uint32_t)0x007e6ae1;

// ─── LORAWAN PARAMS ──────────────────────────────────────────────────────────
uint16_t userChannelsMask[6] = { 0xFF00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000 };

LoRaMacRegion_t loraWanRegion = ACTIVE_REGION;
DeviceClass_t   loraWanClass  = LORAWAN_CLASS;

uint32_t appTxDutyCycle   = 15000;  // 15 segundos
bool overTheAirActivation = LORAWAN_NETMODE;
bool loraWanAdr           = LORAWAN_ADR;
bool keepNet              = LORAWAN_NET_RESERVE;
bool isTxConfirmed        = LORAWAN_UPLINKMODE;
uint8_t appPort           = 2;
uint8_t confirmedNbTrials = 4;

// ─── PINES SENSOR ────────────────────────────────────────────────────────────
#define PinTrig  GPIO1
#define PinEcho  GPIO2
#define NUM_MUESTRAS  5

// ─── SENSOR JSN-SR04T ────────────────────────────────────────────────────────
float medirDistanciaCM() {
    float suma = 0;
    int validas = 0;

    for (int i = 0; i < NUM_MUESTRAS; i++) {
        digitalWrite(PinTrig, LOW);
        delayMicroseconds(2);
        digitalWrite(PinTrig, HIGH);
        delayMicroseconds(10);
        digitalWrite(PinTrig, LOW);

        unsigned long tiempo = pulseIn(PinEcho, HIGH);
        float distancia = tiempo * 0.000001 * 34000.0 / 2.0;

        if (distancia > 2.0 && distancia < 500.0) {
            Serial.print("  Muestra: ");
            Serial.print(distancia);
            Serial.println(" cm");
            suma += distancia;
            validas++;
        }
        delay(50);
    }

    if (validas == 0) return -1.0;
    return suma / validas;
}

// ─── PREPARAR PAYLOAD ────────────────────────────────────────────────────────
void prepareTxFrame(uint8_t port) {
    float dist_cm = medirDistanciaCM();
    uint16_t batt_mv = (uint16_t)getBatteryVoltage();

    if (dist_cm < 0) {
        Serial.println("Sensor: sin lectura valida");
        dist_cm = 0;
    }

    uint16_t dist_mm = (uint16_t)(dist_cm * 10.0);
    int batt_pct = (int)(((float)batt_mv - 3300.0) / (4200.0 - 3300.0) * 100.0);
    if (batt_pct > 100) batt_pct = 100;
    if (batt_pct < 0)   batt_pct = 0;

    Serial.print("Distancia: "); Serial.print(dist_cm);
    Serial.print(" cm | Bateria: "); Serial.print(batt_pct);
    Serial.print("% ("); Serial.print(batt_mv);
    Serial.println(" mV)");

    appData[0] = (dist_mm >> 8) & 0xFF;
    appData[1] = dist_mm & 0xFF;
    appData[2] = (batt_mv >> 8) & 0xFF;
    appData[3] = batt_mv & 0xFF;
    appDataSize = 4;

    Serial.println("Payload Tipo A - 4 bytes");
}

// ─── SETUP / LOOP ────────────────────────────────────────────────────────────
void setup() {
    boardInitMcu();
    Serial.begin(115200);

    pinMode(PinTrig, OUTPUT);
    pinMode(PinEcho, INPUT);
    digitalWrite(PinTrig, LOW);

    Serial.println("\n=== AquaAlert CubeCell v1.0 ===");

    deviceState = DEVICE_STATE_INIT;
}

void loop() {
    switch (deviceState) {
        case DEVICE_STATE_INIT: {
#if(LORAWAN_DEVEUI_AUTO)
            LoRaWAN.generateDeveuiByChipID();
#endif
            printDevParam();
            LoRaWAN.init(loraWanClass, loraWanRegion);
            deviceState = DEVICE_STATE_JOIN;
            break;
        }
        case DEVICE_STATE_JOIN: {
            Serial.println("Conectando...");
            LoRaWAN.join();
            break;
        }
        case DEVICE_STATE_SEND: {
            prepareTxFrame(appPort);
            LoRaWAN.send();
            deviceState = DEVICE_STATE_CYCLE;
            break;
        }
        case DEVICE_STATE_CYCLE: {
            txDutyCycleTime = appTxDutyCycle + randr(0, APP_TX_DUTYCYCLE_RND);
            LoRaWAN.cycle(txDutyCycleTime);
            deviceState = DEVICE_STATE_SLEEP;
            break;
        }
        case DEVICE_STATE_SLEEP: {
            LoRaWAN.sleep();
            break;
        }
        default: {
            deviceState = DEVICE_STATE_INIT;
            break;
        }
    }
}
