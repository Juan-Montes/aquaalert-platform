from sqlalchemy import (
    Column, String, Float, Boolean,
    DateTime, Text, func
)
from app.core.database import Base


class Device(Base):
    """
    Registro de nodos LoRaWAN.
    Aquí se guarda la configuración de cada sensor
    (altura del puente, umbrales, ubicación, etc.)
    """
    __tablename__ = "devices"

    # ─── PK: Device EUI (16 chars hex) ────────────────
    device_eui = Column(String(16), primary_key=True, nullable=False)

    # ─── Info general ─────────────────────────────────
    name = Column(String(100), nullable=False, default="Sin nombre")
    description = Column(Text, nullable=True)
    location_name = Column(String(200), nullable=True)  # Ej: "Puente Guadalupe"

    # ─── Coordenadas GPS ──────────────────────────────
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # ─── Configuración física del sensor ──────────────
    # Altura desde el sensor hasta el nivel CERO del río (fondo / lecho)
    bridge_height_cm = Column(Float, nullable=False, default=300.0)

    # ─── Umbrales de alerta (personalizables) ─────────
    threshold_watch_pct = Column(Float, default=50.0)    # 🟡 50%
    threshold_warning_pct = Column(Float, default=70.0)  # 🟠 70%
    threshold_critical_pct = Column(Float, default=85.0) # 🔴 85%

    # ─── Estado ───────────────────────────────────────
    is_active = Column(Boolean, default=True, nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    # ─── Auditoría ────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<Device eui={self.device_eui} "
            f"name='{self.name}' "
            f"active={self.is_active}>"
        )
