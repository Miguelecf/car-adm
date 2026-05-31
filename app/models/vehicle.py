from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class VehicleStatus(str, enum.Enum):
    ACTIVO = "activo"
    EN_TALLER = "en_taller"
    FUERA_SERVICIO = "fuera_servicio"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer)
    plate = Column(String(20), unique=True, nullable=False, index=True)
    color = Column(String(30))
    current_km = Column(Integer, default=0)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.ACTIVO)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())