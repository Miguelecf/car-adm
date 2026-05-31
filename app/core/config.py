from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "car-adm"
    DATABASE_URL: str = "sqlite:///./car_adm.db"
    PAYMENT_DAY: int = 1
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()