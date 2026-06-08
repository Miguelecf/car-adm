from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, Text
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.models.soft_delete import SoftDeleteMixin


class MaintenanceType(str, enum.Enum):
    ACEITE = "aceite"
    FILTROS = "filtros"
    FRENOS = "frenos"
    LLANTAS = "llantas"
    CORREA = "correa"
    OTRO = "otro"


class Maintenance(SoftDeleteMixin, Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    type = Column(Enum(MaintenanceType), nullable=False)
    description = Column(Text)
    km_at_service = Column(Integer, nullable=False)
    service_date = Column(Date, nullable=False)
    cost = Column(Integer, default=0)
    next_service_km = Column(Integer)
    next_service_date = Column(Date)

    vehicle = relationship("Vehicle")
