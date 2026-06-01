from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Maintenance, MaintenanceType
from app.services.maintenance_service import MaintenanceService
from app.services.vehicle_service import VehicleService
from app.web.templates import templates


router = APIRouter()


def maintenance_to_dict(m: Maintenance) -> dict:
    return {
        "id": m.id,
        "vehicle_id": m.vehicle_id,
        "vehicle_plate": m.vehicle.plate if m.vehicle else "",
        "type": m.type.value if hasattr(m.type, 'value') else m.type,
        "description": m.description or "",
        "km_at_service": m.km_at_service,
        "service_date": m.service_date.strftime("%Y-%m-%d") if m.service_date else "",
        "cost": m.cost,
        "next_service_km": m.next_service_km,
        "next_service_date": m.next_service_date.strftime("%Y-%m-%d") if m.next_service_date else "",
    }


@router.get("/maintenance", response_class=HTMLResponse)
async def list_maintenance(request: Request, db: Session = Depends(get_db)):
    service = MaintenanceService(db)
    records = service.get_all()
    return templates.TemplateResponse(request, "pages/maintenance/list.html", {
        "maintenances": [maintenance_to_dict(m) for m in records],
        "current_path": "/maintenance",
    })


@router.get("/maintenance/new", response_class=HTMLResponse)
async def new_maintenance_form(request: Request, db: Session = Depends(get_db)):
    vehicle_service = VehicleService(db)
    return templates.TemplateResponse(request, "pages/maintenance/form.html", {
        "maintenance": None,
        "vehicles": vehicle_service.get_all(),
        "action": "/maintenance",
        "current_path": "/maintenance",
    })


@router.post("/maintenance")
async def create_maintenance(
    request: Request,
    vehicle_id: int = Form(...),
    type: str = Form(...),
    description: str = Form(""),
    km_at_service: int = Form(...),
    service_date: str = Form(...),
    cost: int = Form(0),
    next_service_km: int = Form(0),
    next_service_date: str = Form(""),
    db: Session = Depends(get_db),
):
    from datetime import date
    service = MaintenanceService(db)
    vehicle_service = VehicleService(db)

    next_date = None
    if next_service_date:
        next_date = date.fromisoformat(next_service_date)

    maintenance = service.create({
        "vehicle_id": vehicle_id,
        "type": MaintenanceType(type),
        "description": description,
        "km_at_service": km_at_service,
        "service_date": date.fromisoformat(service_date),
        "cost": cost,
        "next_service_km": next_service_km if next_service_km else None,
        "next_service_date": next_date,
    })

    if next_service_km:
        vehicle_service.update_km(vehicle_id, km_at_service)

    records = service.get_all()
    return templates.TemplateResponse(request, "pages/maintenance/table.html", {
        "maintenances": [maintenance_to_dict(m) for m in records],
    })


@router.delete("/maintenance/{maintenance_id}")
async def delete_maintenance(request: Request, maintenance_id: int, db: Session = Depends(get_db)):
    service = MaintenanceService(db)
    service.delete(maintenance_id)
    records = service.get_all()
    return templates.TemplateResponse(request, "pages/maintenance/table.html", {
        "maintenances": [maintenance_to_dict(m) for m in records],
    })