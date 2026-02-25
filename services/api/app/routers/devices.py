from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.device import Device

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────
class DeviceCreate(BaseModel):
    device_eui: str
    name: str
    description: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bridge_height_cm: float = 300.0
    threshold_watch_pct: float = 50.0
    threshold_warning_pct: float = 70.0
    threshold_critical_pct: float = 85.0


class DeviceOut(DeviceCreate):
    is_active: bool
    last_seen: Optional[str]

    class Config:
        from_attributes = True


# ─── Endpoints ────────────────────────────────────────

@router.get("/", response_model=list[DeviceOut])
async def list_devices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device))
    return result.scalars().all()


@router.post("/", response_model=DeviceOut, status_code=201)
async def create_device(
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registra un nuevo nodo sensor."""
    # Normalizar EUI siempre a mayúsculas
    data.device_eui = data.device_eui.upper()

    # Verificar si ya existe
    existing = await db.get(Device, data.device_eui)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Device EUI '{data.device_eui}' ya está registrado"
        )

    device = Device(**data.model_dump())
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.get("/{device_eui}", response_model=DeviceOut)
async def get_device(
    device_eui: str,
    db: AsyncSession = Depends(get_db)
):
    device = await db.get(Device, device_eui)
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device


@router.patch("/{device_eui}", response_model=DeviceOut)
async def update_device(
    device_eui: str,
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza configuración de un nodo (altura puente, umbrales)."""
    device = await db.get(Device, device_eui)
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(device, field, value)

    await db.commit()
    await db.refresh(device)
    return device


@router.delete("/{device_eui}", status_code=204)
async def delete_device(
    device_eui: str,
    db: AsyncSession = Depends(get_db)
):
    device = await db.get(Device, device_eui)
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    device.is_active = False  # Soft delete
    await db.commit()
