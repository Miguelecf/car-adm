from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    
    APP_NAME: str = "car-adm"
    DATABASE_URL: str = "sqlite:///./car_adm.db"
    PAYMENT_DAY: int = 1
    DEBUG: bool = True


settings = Settings()