"""
Cliente MQTT asíncrono para AquaAlert.
Se suscribe a los uplinks de ChirpStack y procesa
cada mensaje: decodifica payload, calcula nivel de agua,
evalúa alertas y persiste en TimescaleDB.

Topic ChirpStack v4:
  application/{app_id}/device/{dev_eui}/event/up
"""
import asyncio
import base64
import json
from datetime import datetime, timezone

import aiomqtt
import structlog
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db_session
from app.models.device import Device
from app.models.reading import SensorReading
from app.services.alert_service import evaluate_alert_level, send_telegram_alert
from app.services.decoder import decode_payload

logger = structlog.get_logger()

# Topic wildcard — escucha todos los devices de todas las apps
UPLINK_TOPIC = "application/+/device/+/event/up"


class MQTTClient:
    """
    Maneja la conexión al broker MQTT y el procesamiento
    de uplinks LoRaWAN desde ChirpStack.
    """

    def __init__(self):
        self._task: asyncio.Task | None = None

    async def connect(self):
        """Inicia la escucha de mensajes MQTT en background."""
        self._task = asyncio.create_task(self._listen())
        logger.info("mqtt.listener_started", topic=UPLINK_TOPIC)

    async def disconnect(self):
        """Cancela la tarea de escucha limpiamente."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("mqtt.listener_stopped")

    async def _listen(self):
        """
        Loop principal: conecta al broker y procesa
        mensajes indefinidamente con reconexión automática.
        """
        while True:
            try:
                async with aiomqtt.Client(
                    hostname=settings.MQTT_BROKER,
                    port=settings.MQTT_PORT,
                    username=settings.MQTT_USER or None,
                    password=settings.MQTT_PASSWORD or None,
                ) as client:
                    logger.info(
                        "mqtt.connected",
                        broker=settings.MQTT_BROKER,
                        port=settings.MQTT_PORT,
                    )
                    await client.subscribe(UPLINK_TOPIC)

                    async for message in client.messages:
                        await self._process_message(
                            topic=str(message.topic),
                            payload=message.payload,
                        )

            except aiomqtt.MqttError as e:
                logger.warning(
                    "mqtt.connection_lost",
                    error=str(e),
                    retry_in=5,
                )
                await asyncio.sleep(5)  # Reconectar en 5s

    async def _process_message(self, topic: str, payload: bytes):
        """
        Procesa un uplink de ChirpStack:
        1. Parsea JSON del mensaje
        2. Decodifica payload base64 del sensor
        3. Calcula nivel de agua con altura del puente
        4. Evalúa nivel de alerta según umbrales del device
        5. Persiste SensorReading en TimescaleDB
        6. Envía alerta Telegram si es necesario
        """
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("mqtt.invalid_json", topic=topic)
            return

        # Extraer device EUI del mensaje ChirpStack
        device_eui = (
            data.get("deviceInfo", {}).get("devEui", "")
            or data.get("devEUI", "")
        ).upper()

        if not device_eui:
            logger.warning("mqtt.no_device_eui", topic=topic)
            return

        # Decodificar payload base64 → bytes del sensor
        raw_b64 = data.get("data", "")
        if not raw_b64:
            logger.warning("mqtt.empty_payload", device=device_eui)
            return

        raw_bytes = base64.b64decode(raw_b64)
        decoded = decode_payload(raw_bytes)

        if not decoded:
            logger.warning("mqtt.decode_failed", device=device_eui)
            return

        # Señal LoRa
        rx_info = data.get("rxInfo", [{}])[0]
        rssi = rx_info.get("rssi")
        snr  = rx_info.get("snr")

        async with get_db_session() as db:
            # Buscar configuración del dispositivo
            result = await db.execute(
                select(Device).where(Device.device_eui == device_eui)
            )
            device = result.scalar_one_or_none()

            if not device:
                logger.warning(
                    "mqtt.unknown_device",
                    device=device_eui,
                    hint="Register it via POST /api/v1/devices",
                )
                return

            # Calcular nivel de agua
            distance_cm  = decoded["distance_cm"]
            water_level  = max(0.0, device.bridge_height_cm - distance_cm)
            fill_pct     = min(100.0, (water_level / device.bridge_height_cm) * 100)
            alert_level  = evaluate_alert_level(fill_pct, device)

            # Persistir lectura
            reading = SensorReading(
                device_eui    = device_eui,
                time          = datetime.now(timezone.utc),
                distance_cm   = distance_cm,
                water_level_cm= water_level,
                fill_pct      = fill_pct,
                battery_mv    = decoded["battery_mv"],
                battery_pct   = decoded["battery_pct"],
                rssi          = rssi,
                snr           = snr,
                alert_level   = alert_level,
            )
            db.add(reading)

            # Actualizar last_seen del device
            device.last_seen = reading.time

            logger.info(
                "reading.saved",
                device=device_eui,
                water_level_cm=water_level,
                fill_pct=round(fill_pct, 1),
                alert=alert_level,
                battery_pct=decoded["battery_pct"],
            )

        # Enviar alerta Telegram (fuera de la sesión DB)
        if alert_level != "NORMAL":
            await send_telegram_alert(
                device       = device,
                water_level_cm=water_level,
                fill_pct     = fill_pct,
                alert_level  = alert_level,
                battery_pct  = decoded["battery_pct"],
            )
