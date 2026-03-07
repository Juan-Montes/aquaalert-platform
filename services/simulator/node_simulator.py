"""
Simulador de nodo CubeCell AB02S + JSN-SR04T con GPS Air530
Publica uplinks MQTT simulando el formato ChirpStack

Payload tipo A (4 bytes)  — sin GPS, cada uplink normal
Payload tipo B (12 bytes) — con GPS, cada GPS_INTERVAL uplinks
"""

import asyncio
import base64
import json
import os
import random
import struct
import time

import aiomqtt

# ─── Configuración ────────────────────────────────────
MQTT_BROKER   = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT     = int(os.getenv("MQTT_PORT", "1883"))
DEVICE_EUI    = os.getenv("DEVICE_EUI", "a840411d3181bd6b")
SIM_INTERVAL  = int(os.getenv("SIM_INTERVAL", "30"))
GPS_INTERVAL  = int(os.getenv("GPS_INTERVAL", "10"))  # cada N uplinks enviar GPS

# ─── Ubicación base del sensor (puente simulado) ──────
# Coordenadas del Puente Guadalajara — ajustar al puente real
BASE_LAT = float(os.getenv("SIM_LAT",  "20.659700"))
BASE_LON = float(os.getenv("SIM_LON", "-103.349600"))
GPS_NOISE = 0.000050  # ~5 metros de ruido GPS

# ─── Escenarios de nivel de agua ─────────────────────
SCENARIOS = [
    ("normal",   2000, 2800, 70),   # distancia alta = nivel bajo
    ("watch",    1500, 1999, 15),   # nivel subiendo
    ("warning",   900, 1499, 10),   # nivel alto
    ("critical",  300,  899,  5),   # nivel crítico
]


def make_payload_a(distance_mm: int, battery_mv: int) -> bytes:
    """Payload tipo A — 4 bytes sin GPS."""
    return struct.pack(">HH", distance_mm, battery_mv)


def make_payload_b(distance_mm: int, battery_mv: int,
                   lat: float, lon: float) -> bytes:
    """Payload tipo B — 12 bytes con GPS."""
    return struct.pack(
        ">HHii",
        distance_mm,
        battery_mv,
        int(lat * 1_000_000),
        int(lon * 1_000_000),
    )


def pick_scenario() -> tuple:
    """Elige escenario aleatoriamente con los pesos definidos."""
    names    = [s[0] for s in SCENARIOS]
    d_mins   = [s[1] for s in SCENARIOS]
    d_maxes  = [s[2] for s in SCENARIOS]
    weights  = [s[3] for s in SCENARIOS]
    idx = random.choices(range(len(SCENARIOS)), weights=weights)[0]
    distance = random.randint(d_mins[idx], d_maxes[idx])
    return names[idx], distance


def gps_with_noise() -> tuple[float, float]:
    """Coordenadas GPS con pequeño ruido para simular movimiento real."""
    lat = BASE_LAT + random.uniform(-GPS_NOISE, GPS_NOISE)
    lon = BASE_LON + random.uniform(-GPS_NOISE, GPS_NOISE)
    return round(lat, 6), round(lon, 6)


def build_chirpstack_message(payload: bytes, device_eui: str) -> dict:
    """Construye mensaje JSON en formato ChirpStack v4 uplink."""
    return {
        "deviceInfo": {
            "deviceEui": device_eui.upper(),
            "deviceName": f"CubeCell-{device_eui[-4:].upper()}",
            "applicationId": "1",
        },
        "data": base64.b64encode(payload).decode(),
        "rxInfo": [{
            "gatewayId": "0016c001ff1a3b4d",
            "rssi": random.randint(-110, -60),
            "snr":  round(random.uniform(-5, 10), 1),
        }],
        "fCnt": int(time.time()) % 65536,
    }


async def main():
    app_id     = "1"
    topic      = f"application/{app_id}/device/{DEVICE_EUI}/event/up"
    uplink_count = 0

    print(f"🚀 Simulador iniciado | Device: {DEVICE_EUI} | "
          f"Intervalo: {SIM_INTERVAL}s | GPS cada {GPS_INTERVAL} uplinks")
    print(f"📍 Ubicación base: {BASE_LAT}, {BASE_LON}")

    async with aiomqtt.Client(hostname=MQTT_BROKER, port=MQTT_PORT) as client:
        while True:
            scenario, distance_mm = pick_scenario()
            battery_mv = random.randint(3300, 4100)
            uplink_count += 1

            # Cada GPS_INTERVAL uplinks → payload con GPS
            send_gps = (uplink_count % GPS_INTERVAL == 0)

            if send_gps:
                lat, lon = gps_with_noise()
                payload = make_payload_b(distance_mm, battery_mv, lat, lon)
                gps_info = f"📍 GPS: {lat:.6f}, {lon:.6f}"
            else:
                payload = make_payload_a(distance_mm, battery_mv)
                gps_info = ""

            message = build_chirpstack_message(payload, DEVICE_EUI)

            timestamp = time.strftime("%H:%M:%S")
            print(
                f"[{timestamp}] #{uplink_count:04d} "
                f"Scenario: {scenario:<8} | "
                f"Dist: {distance_mm}mm | "
                f"Bat: {battery_mv}mV | "
                f"{'📍 GPS' if send_gps else '   ---'} → {topic}"
            )

            await client.publish(topic, json.dumps(message))
            await asyncio.sleep(SIM_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
