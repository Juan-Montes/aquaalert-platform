"""
AquaAlert IoT Platform — API Entry Point
FastAPI application factory con lifespan para
conexión MQTT y base de datos.
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.routers import alerts, devices, sensors, webhooks
from app.services.mqtt_client import MQTTClient

logger = structlog.get_logger()

# ─── Instancia global del cliente MQTT ───────────────
mqtt_client = MQTTClient()


# ─── Lifespan: startup y shutdown de la app ──────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    startup  → init DB + conectar MQTT broker
    shutdown → desconectar MQTT limpiamente
    """
    # ── Startup ───────────────────────────────────────
    logger.info("aquaalert.starting", version=app.version)

    # Crear tablas si no existen
    await init_db()
    logger.info("database.ready")

    # Conectar al broker MQTT y escuchar uplinks
    await mqtt_client.connect()
    logger.info("mqtt.connected", broker=settings.MQTT_BROKER)

    yield  # ← app corriendo

    # ── Shutdown ──────────────────────────────────────
    await mqtt_client.disconnect()
    logger.info("aquaalert.stopped")


# ─── Crear la aplicación FastAPI ─────────────────────
app = FastAPI(
    title="AquaAlert IoT Platform",
    description=(
        "API de monitoreo ambiental en tiempo real basada en LoRaWAN.\n\n"
        "Casos de uso:\n"
        "- 🌊 Alertamiento temprano de inundaciones (nivel de ríos)\n"
        "- 🌱 Automatización de invernaderos hidropónicos\n"
        "- 📡 Red de sensores LoRaWAN con ChirpStack"
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─── CORS ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routers ──────────────────────────────────────────
app.include_router(
    sensors.router,
    prefix="/api/v1/sensors",
    tags=["📊 Sensors"],
)
app.include_router(
    devices.router,
    prefix="/api/v1/devices",
    tags=["📡 Devices"],
)
app.include_router(
    alerts.router,
    prefix="/api/v1/alerts",
    tags=["🚨 Alerts"],
)
app.include_router(
    webhooks.router,
    prefix="/api/v1/webhooks",
    tags=["🔗 Webhooks"],
)


# ─── Endpoints base ───────────────────────────────────
@app.get("/health", tags=["⚙️ System"])
async def health_check():
    """
    Health check para Docker y load balancers.
    Retorna 200 si la API está operativa.
    """
    return {
        "status": "ok",
        "service": "aquaalert-api",
        "version": app.version,
    }


@app.get("/", tags=["⚙️ System"])
async def root():
    """Información general de la API."""
    return {
        "service": "AquaAlert IoT Platform",
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "sensors": "/api/v1/sensors",
            "devices": "/api/v1/devices",
            "alerts":  "/api/v1/alerts",
        },
    }
