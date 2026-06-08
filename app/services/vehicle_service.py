from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Vehicle, VehicleStatus


class VehicleService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Vehicle]:
        return self.db.query(Vehicle).filter(Vehicle.deleted_at.is_(None)).order_by(Vehicle.id.desc()).all()

    def get_by_id(self, vehicle_id: int, include_deleted: bool = False) -> Optional[Vehicle]:
        query = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id)
        if not include_deleted:
            query = query.filter(Vehicle.deleted_at.is_(None))
        return query.first()

    def create(self, data: dict) -> Vehicle:
        vehicle = Vehicle(**data)
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle

    def update(self, vehicle_id: int, data: dict) -> Optional[Vehicle]:
        vehicle = self.get_by_id(vehicle_id)
        if not vehicle:
            return None
        for key, value in data.items():
            setattr(vehicle, key, value)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle

    def delete(self, vehicle_id: int) -> bool:
        vehicle = self.get_by_id(vehicle_id)
        if not vehicle:
            return False
        vehicle.soft_delete(reason="Deleted from vehicles UI")
        self.db.commit()
        return True

    def update_km(self, vehicle_id: int, km: int) -> Optional[Vehicle]:
        vehicle = self.get_by_id(vehicle_id)
        if not vehicle:
            return None
        vehicle.current_km = km
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle
