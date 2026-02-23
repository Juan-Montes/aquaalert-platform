from sqlalchemy import (
    Column, String, Float, Integer,
    DateTime, func, Index
)
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid


class SensorReading(Base):
    """
    Tabla principal de lecturas — hypertable en TimescaleDB.
    Cada fila = 1 uplink LoRaWAN de un nodo sensor.
    """
    __tablename__ = "sensor_readings"

    # ─── PK ───────────────────────────────────────────
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ─── Tiempo (partición TimescaleDB) ───────────────
    time = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # ─── Identificación del dispositivo ───────────────
    device_eui = Column(String(16), nullable=False, index=True)

    # ─── Datos del sensor ultrasónico ─────────────────
    distance_cm = Column(Float, nullable=True)
    # Nivel de agua calculado: altura_puente - distancia
    water_level_cm = Column(Float, nullable=True)
    # Porcentaje de llenado respecto a altura puente
    fill_pct = Column(Float, nullable=True)

    # ─── Estado de la batería ─────────────────────────
    battery_mv = Column(Integer, nullable=True)
    battery_pct = Column(Integer, nullable=True)

    # ─── Calidad de señal LoRa ────────────────────────
    rssi = Column(Integer, nullable=True)   # dBm
    snr = Column(Float, nullable=True)      # dB

    # ─── Nivel de alerta en el momento de la lectura ──
    alert_level = Column(
        String(10),
        nullable=False,
        default="NORMAL"
    )  # NORMAL | WATCH | WARNING | CRITICAL

    # ─── Índice compuesto para queries frecuentes ─────
    __table_args__ = (
        Index("ix_readings_device_time", "device_eui", "time"),
    )

    def __repr__(self):
        return (
            f"<SensorReading "
            f"device={self.device_eui} "
            f"dist={self.distance_cm}cm "
            f"level={self.alert_level} "
            f"t={self.time}>"
        )
