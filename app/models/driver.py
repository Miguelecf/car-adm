from sqlalchemy import Column, Integer, String, Date
from app.core.database import Base
from app.models.soft_delete import SoftDeleteMixin


class Driver(SoftDeleteMixin, Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    address = Column(String(200))
    license_number = Column(String(50))
    license_expiry = Column(Date)
