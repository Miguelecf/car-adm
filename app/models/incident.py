from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, Text
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class IncidentType(str, enum.Enum):
    MULTA = "multa"
    ACCIDENTE = "accidente"
    RECLAMO = "reclamo"


class IncidentStatus(str, enum.Enum):
    PENDIENTE = "pendiente"
    RESUELTO = "resuelto"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    type = Column(Enum(IncidentType), nullable=False)
    description = Column(Text)
    date = Column(Date, nullable=False)
    cost = Column(Integer, default=0)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.PENDIENTE)

    vehicle = relationship("Vehicle")
    driver = relationship("Driver")