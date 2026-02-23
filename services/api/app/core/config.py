from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import list


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── API ──────────────────────────────────────────
    API_DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # ─── Base de datos (TimescaleDB) ──────────────────
    TIMESCALE_USER: str = "aquaalert"
    TIMESCALE_PASSWORD: str = "changeme"
    TIMESCALE_DB: str = "aquaalert_ts"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.TIMESCALE_USER}:"
            f"{self.TIMESCALE_PASSWORD}@timescaledb:5432/{self.TIMESCALE_DB}"
        )

    # ─── MQTT ─────────────────────────────────────────
    MQTT_BROKER: str = "mosquitto"
    MQTT_PORT: int = 1883
    MQTT_USER: str = ""
    MQTT_PASSWORD: str = ""

    # ─── Redis ────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379"

    # ─── Telegram ─────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # ─── ChirpStack ───────────────────────────────────
    CHIRPSTACK_API_TOKEN: str = ""


settings = Settings()
