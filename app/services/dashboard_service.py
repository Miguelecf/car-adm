from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Vehicle, VehicleStatus, Contract, ContractStatus
from app.models import Payment, PaymentStatus, Maintenance, Document, Incident, IncidentStatus
from app.services.payment_service import PaymentService
from app.services.maintenance_service import MaintenanceService
from app.services.document_service import DocumentService


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self) -> dict:
        vehicles = self.db.query(Vehicle).filter(Vehicle.deleted_at.is_(None)).all()
        active_contracts = (
            self.db.query(Contract)
            .filter(Contract.status == ContractStatus.ACTIVO, Contract.deleted_at.is_(None))
            .all()
        )
        payment_service = PaymentService(self.db)
        maintenance_service = MaintenanceService(self.db)
        document_service = DocumentService(self.db)

        pending_incidents = (
            self.db.query(Incident)
            .filter(Incident.status == IncidentStatus.PENDIENTE, Incident.deleted_at.is_(None))
            .all()
        )

        total_revenue = payment_service.get_weekly_revenue()
        pending_amount = payment_service.get_pending_amount()

        return {
            "vehicles": {
                "total": len(vehicles),
                "active": len([v for v in vehicles if v.status == VehicleStatus.ACTIVO]),
                "in_repair": len([v for v in vehicles if v.status == VehicleStatus.EN_TALLER]),
                "out_of_service": len([v for v in vehicles if v.status == VehicleStatus.FUERA_SERVICIO]),
            },
            "contracts": {
                "total": len(self.db.query(Contract).filter(Contract.deleted_at.is_(None)).all()),
                "active": len(active_contracts),
            },
            "weekly_revenue": total_revenue,
            "pending_amount": pending_amount,
            "alerts": {
                "total": len(pending_incidents)
                         + len(maintenance_service.get_upcoming())
                         + len(document_service.get_upcoming()),
                "documents": len(document_service.get_upcoming()),
                "maintenance": len(maintenance_service.get_upcoming()),
                "incidents": len(pending_incidents),
            },
        }

    def get_upcoming_maintenance(self) -> list[dict]:
        maintenance_service = MaintenanceService(self.db)
        upcoming = maintenance_service.get_upcoming(days=30)
        result = []
        today = date.today()

        for m in upcoming:
            days_left = None
            if m.next_service_date:
                days_left = (m.next_service_date - today).days
            urgent = days_left is not None and days_left <= 7

            result.append({
                "vehicle": m.vehicle.plate if m.vehicle else "N/A",
                "type": m.type.value if hasattr(m.type, 'value') else m.type,
                "next_date": m.next_service_date.strftime("%d/%m/%Y") if m.next_service_date else None,
                "next_km": m.next_service_km,
                "days_left": days_left,
                "urgent": urgent,
            })
        return result[:5]

    def get_upcoming_documents(self) -> list[dict]:
        document_service = DocumentService(self.db)
        upcoming = document_service.get_upcoming(days=60)
        result = []
        today = date.today()

        for d in upcoming:
            days_left = (d.expiry_date - today).days
            urgent = days_left <= 15

            result.append({
                "vehicle": d.vehicle.plate if d.vehicle else "N/A",
                "type": d.type.value if hasattr(d.type, 'value') else d.type,
                "expiry_date": d.expiry_date.strftime("%d/%m/%Y"),
                "days_left": days_left,
                "urgent": urgent,
            })
        return result[:5]

    def get_profitability(self) -> list[dict]:
        vehicles = self.db.query(Vehicle).filter(Vehicle.deleted_at.is_(None)).all()
        result = []

        for v in vehicles:
            total_revenue = 0
            total_expenses = 0

            contracts = (
                self.db.query(Contract)
                .filter(Contract.vehicle_id == v.id, Contract.status == ContractStatus.ACTIVO, Contract.deleted_at.is_(None))
                .all()
            )
            for c in contracts:
                payments = (
                    self.db.query(Payment)
                    .filter(Payment.contract_id == c.id, Payment.status == PaymentStatus.PAGADO, Payment.deleted_at.is_(None))
                    .all()
                )
                total_revenue += sum(p.amount for p in payments)

            maintenances = (
                self.db.query(Maintenance)
                .filter(Maintenance.vehicle_id == v.id, Maintenance.deleted_at.is_(None))
                .all()
            )
            total_expenses += sum(m.cost or 0 for m in maintenances)

            incidents = (
                self.db.query(Incident)
                .filter(Incident.vehicle_id == v.id, Incident.deleted_at.is_(None))
                .all()
            )
            total_expenses += sum(i.cost or 0 for i in incidents)

            profit = total_revenue - total_expenses
            max_val = max(total_revenue, 1)
            bar_width = int((total_revenue - total_expenses) / max_val * 100) if total_revenue > 0 else 0

            result.append({
                "vehicle": v.plate,
                "revenue": total_revenue,
                "expenses": total_expenses,
                "profit": profit,
                "bar_width": max(0, min(100, bar_width + 50)),
            })

        return sorted(result, key=lambda x: x["profit"], reverse=True)[:5]

    def get_pending_payments(self) -> list[dict]:
        payment_service = PaymentService(self.db)
        overdue = payment_service.get_overdue()
        result = []

        for p in overdue:
            if p.contract:
                result.append({
                    "driver": p.contract.driver.name if p.contract.driver else "N/A",
                    "vehicle": p.contract.vehicle.plate if p.contract.vehicle else "N/A",
                    "amount": p.amount,
                    "due_date": p.due_date.strftime("%d/%m/%Y"),
                })

        return result[:5]
