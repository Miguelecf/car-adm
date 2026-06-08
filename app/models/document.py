from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
from app.models.soft_delete import SoftDeleteMixin


class DocumentType(str, enum.Enum):
    SEGURO = "seguro"
    ITV = "itv"
    MATRICULA = "matricula"


class DocumentStatus(str, enum.Enum):
    VIGENTE = "vigente"
    VENCIDO = "vencido"
    PROXIMO_VENCER = "proximo_a_vencer"


class Document(SoftDeleteMixin, Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    type = Column(Enum(DocumentType), nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    file_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    vehicle = relationship("Vehicle")
