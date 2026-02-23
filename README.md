# 🌊 AquaAlert IoT Platform

Plataforma de monitoreo ambiental en tiempo real basada en **LoRaWAN + FastAPI + TimescaleDB + ChirpStack**.

## Stack

| Servicio | Tecnología | Puerto |
|---|---|---|
| API REST | FastAPI (Python 3.12) | 8000 |
| Red LoRaWAN | ChirpStack v4 | 8080 |
| MQTT Broker | Eclipse Mosquitto | 1883 |
| Time-series DB | TimescaleDB (PG15) | 5433 |
| Cache | Redis 7 | 6379 |
| Dashboards | Grafana 10 | 3000 |

## Inicio rápido

```bash
# 1. Clonar repo
git clone https://github.com/TU_USUARIO/aquaalert-platform.git
cd aquaalert-platform

# 2. Configurar entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar stack
docker compose up -d

# 4. Ver estado
docker compose ps

# 5. Acceder a servicios
# API Docs  → http://localhost:8000/docs
# ChirpStack → http://localhost:8080  (admin/admin)
# Grafana   → http://localhost:3000
```

## Arquitectura

```
Nodo CubeCell (JSN-SR04T)
    ↓ LoRaWAN 915MHz
Gateway Dragino DLOS8N
    ↓ UDP 1700
ChirpStack Network Server
    ↓ MQTT
FastAPI Backend
    ├── TimescaleDB (almacenamiento)
    ├── Redis (cache)
    └── Telegram Bot (alertas)
         ↓
      Grafana Dashboard
```

## Hardware soportado

- **Actual:** Heltec CubeCell AB01/AB02 + JSN-SR04T
- **Próximo:** RAK4631 + RAK5811 + RAK5005-O (WisBlock)

## Casos de uso

- 🌊 Monitoreo de nivel de ríos (alerta temprana inundaciones)
- 🌱 Automatización de invernaderos hidropónicos
- 🏔️ Detección de deslizamientos (extensible)

## Licencia

MIT — Proyecto open source desarrollado en Guadalajara, Jalisco, México.
test
