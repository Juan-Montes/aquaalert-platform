# services/simulator/node_simulator.py
import asyncio
import json
import struct
import base64
import random
import os
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

MQTT_BROKER  = os.getenv("MQTT_BROKER", "localhost")
DEVICE_EUI   = os.getenv("DEVICE_EUI", "a840411d3181bd6b")
APP_EUI      = os.getenv("APP_EUI",    "0000000000000001")
INTERVAL     = int(os.getenv("SIM_INTERVAL", "30"))

def build_chirpstack_uplink(distance_mm: int, battery_mv: int) -> dict:
    """Simula el JSON que ChirpStack publica en MQTT"""
    
    # Payload: 2 bytes distancia + 2 bytes batería
    raw = struct.pack(">HH", distance_mm, battery_mv)
    
    return {
        "deviceInfo": {
            "devEui": DEVICE_EUI,
            "deviceName": "SIM-RioSensor-01",
            "applicationId": "1",
        },
        "data": base64.b64encode(raw).decode(),
        "rxInfo": [{
            "rssi": random.randint(-110, -65),
            "snr":  round(random.uniform(-5, 10), 1),
            "gatewayId": "a840411fffe1bd6b",
        }],
        "fCnt": random.randint(1, 10000),
        "time": datetime.now(timezone.utc).isoformat(),
    }

def simulate_scenario(scenario: str = "normal") -> tuple[int, int]:
    """Diferentes escenarios de prueba"""
    scenarios = {
        "normal":    (2500, 3800),  # Río bajo, batería OK
        "rising":    (1800, 3700),  # Nivel subiendo
        "warning":   (900,  3600),  # Alerta amarilla
        "critical":  (400,  3400),  # Alerta roja
        "low_bat":   (2000, 3100),  # Batería baja
    }
    dist_mm_base, bat_mv_base = scenarios.get(scenario, scenarios["normal"])
    
    # Añadir ruido realista
    dist_mm = dist_mm_base + random.randint(-50, 50)
    bat_mv  = bat_mv_base  + random.randint(-20, 20)
    
    return dist_mm, bat_mv

async def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER, 1883)
    client.loop_start()
    
    print(f"🚀 Simulador iniciado | Device: {DEVICE_EUI} | Intervalo: {INTERVAL}s")
    
    # Simula un escenario de crecida progresiva
    scenario_cycle = ["normal", "normal", "rising", "rising", "warning", "critical"]
    cycle_idx = 0
    
    while True:
        scenario = scenario_cycle[cycle_idx % len(scenario_cycle)]
        distance_mm, battery_mv = simulate_scenario(scenario)
        
        payload = build_chirpstack_uplink(distance_mm, battery_mv)
        topic = f"application/1/device/{DEVICE_EUI}/event/up"
        
        client.publish(topic, json.dumps(payload))
        
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"Scenario: {scenario:10s} | "
            f"Dist: {distance_mm:4d}mm | "
            f"Bat: {battery_mv}mV → {topic}"
        )
        
        cycle_idx += 1
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
