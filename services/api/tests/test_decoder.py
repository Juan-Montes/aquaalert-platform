import pytest
import struct
from app.services.decoder import decode_payload


def build_payload(distance_mm: int, battery_mv: int) -> bytes:
    """Helper: construye bytes como los enviaría el CubeCell"""
    return struct.pack(">HH", distance_mm, battery_mv)


class TestDecodePayload:

    def test_normal_reading(self):
        """Lectura normal: río bajo, batería OK"""
        raw = build_payload(distance_mm=2500, battery_mv=3800)
        result = decode_payload(raw)

        assert result["distance_cm"] == 250.0
        assert result["battery_mv"] == 3800
        assert result["battery_pct"] == 66  # (3800-3000)/(4200-3000)*100

    def test_critical_level(self):
        """Distancia muy corta = río cerca del sensor = nivel crítico"""
        raw = build_payload(distance_mm=400, battery_mv=3700)
        result = decode_payload(raw)

        assert result["distance_cm"] == 40.0
        assert result["battery_mv"] == 3700

    def test_low_battery(self):
        """Batería casi agotada"""
        raw = build_payload(distance_mm=2000, battery_mv=3050)
        result = decode_payload(raw)

        assert result["battery_pct"] <= 5

    def test_full_battery(self):
        """Batería llena"""
        raw = build_payload(distance_mm=2000, battery_mv=4200)
        result = decode_payload(raw)

        assert result["battery_pct"] == 100

    def test_payload_too_short(self):
        """Payload incompleto no debe crashear"""
        result = decode_payload(b"\x00\x01")
        assert result == {}

    def test_empty_payload(self):
        """Payload vacío"""
        result = decode_payload(b"")
        assert result == {}


class TestBatteryCalculation:

    @pytest.mark.parametrize("mv,expected_pct", [
        (4200, 100),
        (3600, 50),
        (3000, 0),
        (2900, 0),   # por debajo del mínimo → clamp a 0
        (4300, 100), # por encima del máximo → clamp a 100
    ])
    def test_battery_pct_range(self, mv: int, expected_pct: int):
        from app.services.decoder import _calc_battery_pct
        assert _calc_battery_pct(mv) == expected_pct
