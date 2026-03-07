"""
Decoder para payload LoRaWAN del nodo CubeCell AB02S + JSN-SR04T

Payload tipo A — 4 bytes (sin GPS, uplink normal):
  Bytes 0-1: distance_mm  uint16 big-endian
  Bytes 2-3: battery_mv   uint16 big-endian

Payload tipo B — 12 bytes (con GPS, cada N uplinks):
  Bytes 0-1:  distance_mm  uint16 big-endian
  Bytes 2-3:  battery_mv   uint16 big-endian
  Bytes 4-7:  latitude     int32  big-endian (grados * 1e6)
  Bytes 8-11: longitude    int32  big-endian (grados * 1e6)

El decoder detecta el tipo por longitud del payload.
"""

import struct
import structlog

log = structlog.get_logger()

BATTERY_MIN_MV = 3000
BATTERY_MAX_MV = 4200


def decode_payload(data: bytes) -> dict:
    """
    Decodifica payload JSN-SR04T con GPS opcional.

    Returns:
        dict con distance_cm, battery_mv, battery_pct
        y opcionalmente latitude, longitude
        o dict vacío si el payload es inválido
    """
    if len(data) not in (4, 12):
        log.warning("decoder.invalid_length", length=len(data))
        return {}

    try:
        distance_mm, battery_mv = struct.unpack_from(">HH", data, 0)
    except struct.error as e:
        log.warning("decoder.unpack_error", error=str(e))
        return {}

    distance_cm  = round(distance_mm / 10, 1)
    battery_pct  = _battery_percent(battery_mv)

    result = {
        "distance_cm": distance_cm,
        "battery_mv":  battery_mv,
        "battery_pct": battery_pct,
        "has_gps":     False,
    }

    # Payload tipo B — incluye GPS
    if len(data) == 12:
        try:
            lat_raw, lon_raw = struct.unpack_from(">ii", data, 4)
            latitude  = round(lat_raw / 1_000_000, 6)
            longitude = round(lon_raw / 1_000_000, 6)

            # Validar rangos geográficos
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                log.warning("decoder.invalid_gps",
                            latitude=latitude, longitude=longitude)
            else:
                result["latitude"]  = latitude
                result["longitude"] = longitude
                result["has_gps"]   = True
                log.debug("decoder.gps_ok",
                          latitude=latitude, longitude=longitude)

        except struct.error as e:
            log.warning("decoder.gps_unpack_error", error=str(e))

    log.debug("decoder.ok",
              distance_cm=distance_cm,
              battery_pct=battery_pct,
              has_gps=result["has_gps"])

    return result


def _battery_percent(battery_mv: int) -> int:
    """Calcula porcentaje de batería en rango 3.0V - 4.2V."""
    pct = (battery_mv - BATTERY_MIN_MV) / (BATTERY_MAX_MV - BATTERY_MIN_MV) * 100
    return max(0, min(100, round(pct)))
