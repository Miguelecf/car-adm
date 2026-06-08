from datetime import date, timedelta
from typing import Optional, Literal
from sqlalchemy.orm import Session
from app.models import Maintenance, MaintenanceType, Vehicle


class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Maintenance]:
        return (
            self.db.query(Maintenance)
            .join(Vehicle)
            .filter(Maintenance.deleted_at.is_(None), Vehicle.deleted_at.is_(None))
            .order_by(Maintenance.service_date.desc())
            .all()
        )

    def get_by_vehicle(self, vehicle_id: int) -> list[Maintenance]:
        return (
            self.db.query(Maintenance)
            .filter(Maintenance.vehicle_id == vehicle_id, Maintenance.deleted_at.is_(None))
            .order_by(Maintenance.service_date.desc())
            .all()
        )

    def get_by_id(self, maintenance_id: int, include_deleted: bool = False) -> Optional[Maintenance]:
        query = self.db.query(Maintenance).filter(Maintenance.id == maintenance_id)
        if not include_deleted:
            query = query.filter(Maintenance.deleted_at.is_(None))
        return query.first()

    def create(self, data: dict) -> Maintenance:
        maintenance = Maintenance(**data)
        self.db.add(maintenance)
        self.db.commit()
        self.db.refresh(maintenance)
        return maintenance

    def update(self, maintenance_id: int, data: dict) -> Optional[Maintenance]:
        maintenance = self.get_by_id(maintenance_id)
        if not maintenance:
            return None
        for key, value in data.items():
            setattr(maintenance, key, value)
        self.db.commit()
        self.db.refresh(maintenance)
        return maintenance

    def delete(self, maintenance_id: int) -> bool:
        maintenance = self.get_by_id(maintenance_id)
        if not maintenance:
            return False
        maintenance.soft_delete(reason="Deleted from maintenance UI")
        self.db.commit()
        return True

    def get_upcoming(self, days: int = 30) -> list[Maintenance]:
        cutoff_date = date.today() + timedelta(days=days)
        cutoff_km_high = 1000000
        cutoff_km_low = 0

        results = []

        by_date = (
            self.db.query(Maintenance)
            .join(Vehicle)
            .filter(
                Maintenance.next_service_date != None,
                Maintenance.deleted_at.is_(None),
                Vehicle.deleted_at.is_(None),
                Maintenance.next_service_date <= cutoff_date,
                Maintenance.next_service_date >= date.today()
            )
            .all()
        )
        results.extend(by_date)

        by_km = (
            self.db.query(Maintenance)
            .join(Vehicle)
            .filter(
                Maintenance.next_service_km != None,
                Maintenance.deleted_at.is_(None),
                Vehicle.deleted_at.is_(None),
                Maintenance.next_service_km <= cutoff_km_high,
                Maintenance.next_service_km > 0
            )
            .all()
        )
        for m in by_km:
            if m not in results:
                results.append(m)

        return sorted(results, key=lambda x: (x.next_service_date or date.today() + timedelta(days=365)))

    def check_vehicle_needs_service(self, vehicle_id: int) -> dict:
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None)).first()
        if not vehicle:
            return {"needs_service": False}

        last = (
            self.db.query(Maintenance)
            .filter(Maintenance.vehicle_id == vehicle_id, Maintenance.deleted_at.is_(None))
            .order_by(Maintenance.service_date.desc())
            .first()
        )

        if not last:
            return {"needs_service": True, "reason": "Sin registro de mantenimiento"}

        reasons = []

        if last.next_service_date and last.next_service_date <= date.today():
            reasons.append(f"Vence: {last.next_service_date}")
        if last.next_service_km and last.next_service_km <= vehicle.current_km:
            reasons.append(f"km: {vehicle.current_km} >= {last.next_service_km}")

        return {"needs_service": bool(reasons), "reason": ", ".join(reasons)}
