from typing import Optional
from sqlalchemy.orm import Session
from app.models import Driver


class DriverService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Driver]:
        return self.db.query(Driver).filter(Driver.deleted_at.is_(None)).order_by(Driver.id.desc()).all()

    def get_by_id(self, driver_id: int, include_deleted: bool = False) -> Optional[Driver]:
        query = self.db.query(Driver).filter(Driver.id == driver_id)
        if not include_deleted:
            query = query.filter(Driver.deleted_at.is_(None))
        return query.first()

    def get_by_dni(self, dni: str) -> Optional[Driver]:
        return self.db.query(Driver).filter(Driver.dni == dni, Driver.deleted_at.is_(None)).first()

    def create(self, data: dict) -> Driver:
        driver = Driver(**data)
        self.db.add(driver)
        self.db.commit()
        self.db.refresh(driver)
        return driver

    def update(self, driver_id: int, data: dict) -> Optional[Driver]:
        driver = self.get_by_id(driver_id)
        if not driver:
            return None
        for key, value in data.items():
            setattr(driver, key, value)
        self.db.commit()
        self.db.refresh(driver)
        return driver

    def delete(self, driver_id: int) -> bool:
        driver = self.get_by_id(driver_id)
        if not driver:
            return False
        driver.soft_delete(reason="Deleted from drivers UI")
        self.db.commit()
        return True
