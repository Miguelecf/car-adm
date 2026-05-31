from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ContractStatus(str, enum.Enum):
    ACTIVO = "activo"
    FINALIZADO = "finalizado"


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    weekly_amount = Column(Integer, nullable=False)
    deposit_amount = Column(Integer, default=0)
    start_km = Column(Integer, nullable=False)
    end_km = Column(Integer)
    status = Column(Enum(ContractStatus), default=ContractStatus.ACTIVO)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    vehicle = relationship("Vehicle")
    driver = relationship("Driver")
    payments = relationship("Payment", back_populates="contract")