from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, Text
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class PaymentMethod(str, enum.Enum):
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"


class PaymentStatus(str, enum.Enum):
    PAGADO = "pagado"
    PENDIENTE = "pendiente"
    ATRASADO = "atrasado"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    method = Column(Enum(PaymentMethod))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDIENTE)
    notes = Column(Text)

    contract = relationship("Contract", back_populates="payments")