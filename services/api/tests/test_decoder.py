import base64
import struct
import pytest
from app.services.decoder import decode_payload


def make_payload_a(distance_mm: int, battery_mv: int) -> bytes:
    """Payload tipo A — 4 bytes sin GPS."""
    return struct.pack(">HH", distance_mm, battery_mv)


def make_payload_b(distance_mm: int, battery_mv: int,
                   lat: float, lon: float) -> bytes:
    """Payload tipo B — 12 bytes con GPS."""
    return struct.pack(">HHii",
                       distance_mm, battery_mv,
                       int(lat * 1_000_000),
                       int(lon * 1_000_000))


# ── Tipo A — sin GPS ──────────────────────────────────

def test_normal_reading():
    payload = make_payload_a(2532, 3800)
    result = decode_payload(payload)
    assert result["distance_cm"] == 253.2
    assert result["battery_mv"]  == 3800
    assert result["battery_pct"] == 67
    assert result["has_gps"]     is False
    assert "latitude"  not in result
    assert "longitude" not in result


def test_min_battery():
    payload = make_payload_a(1000, 3000)
    result = decode_payload(payload)
    assert result["battery_pct"] == 0


def test_max_battery():
    payload = make_payload_a(1000, 4200)
    result = decode_payload(payload)
    assert result["battery_pct"] == 100


def test_battery_clamp_below():
    payload = make_payload_a(1000, 2500)
    result = decode_payload(payload)
    assert result["battery_pct"] == 0


def test_battery_clamp_above():
    payload = make_payload_a(1000, 4500)
    result = decode_payload(payload)
    assert result["battery_pct"] == 100


# ── Tipo B — con GPS ──────────────────────────────────

def test_payload_with_gps():
    payload = make_payload_b(2532, 3800, 20.659699, -103.349609)
    result = decode_payload(payload)
    assert result["distance_cm"] == 253.2
    assert result["battery_pct"] == 67
    assert result["has_gps"]     is True
    assert abs(result["latitude"]  - 20.659699)   < 0.0001
    assert abs(result["longitude"] - (-103.349609)) < 0.0001


def test_gps_guadalajara():
    """Coordenadas reales de Guadalajara, Jalisco."""
    payload = make_payload_b(1500, 3900, 20.6597, -103.3496)
    result = decode_payload(payload)
    assert result["has_gps"] is True
    assert abs(result["latitude"]  - 20.6597)   < 0.001
    assert abs(result["longitude"] - (-103.3496)) < 0.001


def test_invalid_gps_range():
    """GPS fuera de rango geográfico no debe incluirse."""
    payload = make_payload_b(1500, 3900, 999.0, 999.0)
    result = decode_payload(payload)
    assert result["has_gps"] is False
    assert "latitude"  not in result
    assert "longitude" not in result


# ── Payloads inválidos ────────────────────────────────

def test_empty_payload():
    assert decode_payload(b"") == {}


def test_short_payload():
    assert decode_payload(b"\x00\x01\x02") == {}


def test_wrong_length():
    """Longitud 8 no es ni 4 ni 12 — inválido."""
    assert decode_payload(b"\x00" * 8) == {}
