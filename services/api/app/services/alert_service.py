"""
Servicio de alertas para AquaAlert.
Evalúa el nivel de llenado y envía notificaciones
por Telegram cuando se superan los umbrales configurados.
"""
import httpx
import structlog
from app.core.config import settings
from app.models.device import Device

logger = structlog.get_logger()

# ─── Niveles de alerta ────────────────────────────────
ALERT_LEVELS = {
    "NORMAL":   {"emoji": "🟢", "msg": "Nivel normal"},
    "WATCH":    {"emoji": "🟡", "msg": "Nivel en observación"},
    "WARNING":  {"emoji": "🟠", "msg": "Nivel de advertencia"},
    "CRITICAL": {"emoji": "🔴", "msg": "NIVEL CRÍTICO"},
}


def evaluate_alert_level(fill_pct: float, device: Device) -> str:
    """
    Determina el nivel de alerta según el porcentaje
    de llenado y los umbrales configurados por dispositivo.
    """
    if fill_pct >= device.threshold_critical_pct:
        return "CRITICAL"
    if fill_pct >= device.threshold_warning_pct:
        return "WARNING"
    if fill_pct >= device.threshold_watch_pct:
        return "WATCH"
    return "NORMAL"


async def send_telegram_alert(
    device: Device,
    water_level_cm: float,
    fill_pct: float,
    alert_level: str,
    battery_pct: int,
) -> bool:
    """
    Envía notificación a Telegram cuando el nivel
    es WATCH, WARNING o CRITICAL.

    Returns:
        True si el mensaje fue enviado exitosamente.
    """
    if alert_level == "NORMAL":
        return False

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("telegram.not_configured")
        return False

    info = ALERT_LEVELS[alert_level]

    message = (
        f"{info['emoji']} *{info['msg'].upper()}* {info['emoji']}\n\n"
        f"📍 *Sensor:* {device.name}\n"
        f"📌 *Ubicación:* {device.location_name or 'Sin ubicación'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💧 *Nivel de agua:* {water_level_cm:.1f} cm\n"
        f"📊 *Llenado:* {fill_pct:.1f}%\n"
        f"🔋 *Batería:* {battery_pct}%\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 `{device.device_eui}`"
    )

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            })
            response.raise_for_status()
            logger.info(
                "telegram.sent",
                device=device.device_eui,
                level=alert_level,
            )
            return True

    except httpx.HTTPError as e:
        logger.error("telegram.send_failed", error=str(e))
        return False
