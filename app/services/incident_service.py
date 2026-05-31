from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Incident, IncidentType, IncidentStatus, Vehicle, Driver


class IncidentService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Incident]:
        return (
            self.db.query(Incident)
            .join(Vehicle)
            .order_by(Incident.date.desc())
            .all()
        )

    def get_by_vehicle(self, vehicle_id: int) -> list[Incident]:
        return (
            self.db.query(Incident)
            .filter(Incident.vehicle_id == vehicle_id)
            .order_by(Incident.date.desc())
            .all()
        )

    def get_by_driver(self, driver_id: int) -> list[Incident]:
        return (
            self.db.query(Incident)
            .filter(Incident.driver_id == driver_id)
            .order_by(Incident.date.desc())
            .all()
        )

    def get_pending(self) -> list[Incident]:
        return (
            self.db.query(Incident)
            .filter(Incident.status == IncidentStatus.PENDIENTE)
            .order_by(Incident.date.desc())
            .all()
        )

    def get_by_id(self, incident_id: int) -> Optional[Incident]:
        return self.db.query(Incident).filter(Incident.id == incident_id).first()

    def create(self, data: dict) -> Incident:
        incident = Incident(**data)
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def update(self, incident_id: int, data: dict) -> Optional[Incident]:
        incident = self.get_by_id(incident_id)
        if not incident:
            return None
        for key, value in data.items():
            setattr(incident, key, value)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def resolve(self, incident_id: int) -> Optional[Incident]:
        incident = self.get_by_id(incident_id)
        if not incident:
            return None
        incident.status = IncidentStatus.RESUELTO
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def delete(self, incident_id: int) -> bool:
        incident = self.get_by_id(incident_id)
        if not incident:
            return False
        self.db.delete(incident)
        self.db.commit()
        return True

    def get_total_cost(self) -> int:
        return sum(i.cost or 0 for i in self.db.query(Incident).all())