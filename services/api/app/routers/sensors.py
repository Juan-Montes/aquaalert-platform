from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.core.database import get_db
from app.models.reading import SensorReading
from app.models.device import Device

router = APIRouter()


# ─── Schemas de respuesta ─────────────────────────────
class ReadingOut(BaseModel):
    id: str
    time: datetime
    device_eui: str
    distance_cm: Optional[float]
    water_level_cm: Optional[float]
    fill_pct: Optional[float]
    battery_pct: Optional[int]
    rssi: Optional[int]
    snr: Optional[float]
    alert_level: str

    class Config:
        from_attributes = True


class SensorSummary(BaseModel):
    device_eui: str
    name: str
    location_name: Optional[str]
    last_reading: Optional[ReadingOut]
    alert_level: str
    is_active: bool


# ─── Endpoints ────────────────────────────────────────

@router.get("/", response_model=list[SensorSummary])
async def list_sensors(db: AsyncSession = Depends(get_db)):
    """
    Lista todos los dispositivos registrados
    con su última lectura.
    """
    result = await db.execute(
        select(Device).where(Device.is_active.is_(True))
    )
    devices = result.scalars().all()

    summaries = []
    for device in devices:
        # Última lectura del dispositivo
        last_q = await db.execute(
            select(SensorReading)
            .where(SensorReading.device_eui == device.device_eui)
            .order_by(desc(SensorReading.time))
            .limit(1)
        )
        last_reading = last_q.scalar_one_or_none()

        summaries.append(SensorSummary(
            device_eui=device.device_eui,
            name=device.name,
            location_name=device.location_name,
            last_reading=ReadingOut(
                id=str(last_reading.id),
                time=last_reading.time,
                device_eui=last_reading.device_eui,
                distance_cm=last_reading.distance_cm,
                water_level_cm=last_reading.water_level_cm,
                fill_pct=last_reading.fill_pct,
                battery_pct=last_reading.battery_pct,
                rssi=last_reading.rssi,
                snr=last_reading.snr,
                alert_level=last_reading.alert_level,
            ) if last_reading else None,
            alert_level=last_reading.alert_level if last_reading else "NORMAL",
            is_active=device.is_active,
        ))

    return summaries


@router.get("/{device_eui}/readings", response_model=list[ReadingOut])
async def get_readings(
    device_eui: str,
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Historial de lecturas de un sensor.
    Por defecto últimas 24h, máximo 720h (30 días).
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    result = await db.execute(
        select(SensorReading)
        .where(
            SensorReading.device_eui == device_eui,
            SensorReading.time >= since,
        )
        .order_by(desc(SensorReading.time))
        .limit(limit)
    )
    readings = result.scalars().all()

    if not readings:
        raise HTTPException(
            status_code=404,
            detail=f"No hay lecturas para el dispositivo '{device_eui}' en las últimas {hours}h"
        )

    return [
        ReadingOut(
            id=str(r.id),
            time=r.time,
            device_eui=r.device_eui,
            distance_cm=r.distance_cm,
            water_level_cm=r.water_level_cm,
            fill_pct=r.fill_pct,
            battery_pct=r.battery_pct,
            rssi=r.rssi,
            snr=r.snr,
            alert_level=r.alert_level,
        )
        for r in readings
    ]


@router.get("/{device_eui}/latest", response_model=ReadingOut)
async def get_latest(
    device_eui: str,
    db: AsyncSession = Depends(get_db),
):
    """Última lectura de un sensor específico."""
    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.device_eui == device_eui)
        .order_by(desc(SensorReading.time))
        .limit(1)
    )
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(
            status_code=404,
            detail=f"Dispositivo '{device_eui}' no encontrado o sin lecturas"
        )

    return ReadingOut(
        id=str(reading.id),
        time=reading.time,
        device_eui=reading.device_eui,
        distance_cm=reading.distance_cm,
        water_level_cm=reading.water_level_cm,
        fill_pct=reading.fill_pct,
        battery_pct=reading.battery_pct,
        rssi=reading.rssi,
        snr=reading.snr,
        alert_level=reading.alert_level,
    )
