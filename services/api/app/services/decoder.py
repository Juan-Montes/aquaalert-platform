"""
Decoder de payload LoRaWAN para el nodo CubeCell + JSN-SR04T.

Formato del payload (4 bytes, big-endian):
  Bytes 0-1 → distancia en mm  (uint16)
  Bytes 2-3 → voltaje batería  (uint16, en mV)

Ejemplo:
  payload hex: 09 C4 0E D8
  distancia:   0x09C4 = 2500 mm = 250.0 cm
  batería:     0x0ED8 = 3800 mV  = 66%
"""
import struct
from typing import Any

import structlog

logger = structlog.get_logger()

# ─── Constantes de batería LiPo ──────────────────────
BAT_MAX_MV = 4200
BAT_MIN_MV = 3000


def _calc_battery_pct(battery_mv: int) -> int:
    """
    Convierte voltaje LiPo a porcentaje.
    Clamp entre 0% y 100%.
    """
    pct = (battery_mv - BAT_MIN_MV) / (BAT_MAX_MV - BAT_MIN_MV) * 100
    return max(0, min(100, round(pct)))


def decode_payload(raw: bytes) -> dict[str, Any]:
    """
    Decodifica bytes crudos del CubeCell.

    Returns:
        dict con distance_cm, battery_mv, battery_pct
        o dict vacío si el payload es inválido.
    """
    if len(raw) < 4:
        logger.warning("decoder.payload_too_short", length=len(raw))
        return {}

    try:
        distance_mm, battery_mv = struct.unpack(">HH", raw[:4])

        result = {
            "distance_cm":  round(distance_mm / 10, 1),
            "battery_mv":   battery_mv,
            "battery_pct":  _calc_battery_pct(battery_mv),
        }

        logger.debug(
            "decoder.ok",
            distance_cm=result["distance_cm"],
            battery_pct=result["battery_pct"],
        )
        return result

    except struct.error as e:
        logger.error("decoder.unpack_error", error=str(e))
        return {}
