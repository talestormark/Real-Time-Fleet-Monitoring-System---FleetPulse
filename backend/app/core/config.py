from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FleetPulse"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    # Security
    SECRET_KEY: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Event Detection Thresholds
    LOW_BATTERY_THRESHOLD: int = 20
    STALE_DEVICE_THRESHOLD_MINUTES: int = 15
    IMPACT_THRESHOLD_G: float = 3.0

    class Config:
        env_file = ".env"
        case_sensitive = True

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == 'BACKEND_CORS_ORIGINS':
                return json.loads(raw_val)
            return cls.json_loads(raw_val)


settings = Settings()
