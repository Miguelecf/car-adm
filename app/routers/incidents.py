from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Incident, IncidentType, IncidentStatus
from app.services.incident_service import IncidentService
from app.services.vehicle_service import VehicleService
from app.services.driver_service import DriverService
from app.web.templates import templates


router = APIRouter()


def incident_to_dict(i: Incident) -> dict:
    return {
        "id": i.id,
        "vehicle_id": i.vehicle_id,
        "driver_id": i.driver_id,
        "vehicle_plate": i.vehicle.plate if i.vehicle else "",
        "driver_name": i.driver.name if i.driver else "",
        "type": i.type.value if hasattr(i.type, 'value') else i.type,
        "description": i.description or "",
        "date": i.date.strftime("%Y-%m-%d") if i.date else "",
        "cost": i.cost,
        "status": i.status.value if hasattr(i.status, 'value') else i.status,
    }


@router.get("/incidents", response_class=HTMLResponse)
async def list_incidents(request: Request, db: Session = Depends(get_db)):
    service = IncidentService(db)
    incidents = service.get_all()
    return templates.TemplateResponse("pages/incidents/list.html", {
        "request": request,
        "incidents": [incident_to_dict(i) for i in incidents],
        "current_path": "/incidents",
    })


@router.get("/incidents/new", response_class=HTMLResponse)
async def new_incident_form(request: Request, db: Session = Depends(get_db)):
    vehicle_service = VehicleService(db)
    driver_service = DriverService(db)
    return templates.TemplateResponse("pages/incidents/form.html", {
        "request": request,
        "incident": None,
        "vehicles": vehicle_service.get_all(),
        "drivers": driver_service.get_all(),
        "action": "/incidents",
        "current_path": "/incidents",
    })


@router.post("/incidents")
async def create_incident(
    request: Request,
    vehicle_id: int = Form(...),
    driver_id: int = Form(0),
    type: str = Form(...),
    description: str = Form(""),
    date: str = Form(...),
    cost: int = Form(0),
    db: Session = Depends(get_db),
):
    from datetime import date as date_type
    service = IncidentService(db)

    incident = service.create({
        "vehicle_id": vehicle_id,
        "driver_id": driver_id if driver_id else None,
        "type": IncidentType(type),
        "description": description,
        "date": date_type.fromisoformat(date),
        "cost": cost,
        "status": IncidentStatus.PENDIENTE,
    })
    incidents = service.get_all()
    return templates.TemplateResponse("pages/incidents/table.html", {
        "request": request,
        "incidents": [incident_to_dict(i) for i in incidents],
    })


@router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(request: Request, incident_id: int, db: Session = Depends(get_db)):
    service = IncidentService(db)
    service.resolve(incident_id)
    incidents = service.get_all()
    return templates.TemplateResponse("pages/incidents/table.html", {
        "request": request,
        "incidents": [incident_to_dict(i) for i in incidents],
    })


@router.delete("/incidents/{incident_id}")
async def delete_incident(request: Request, incident_id: int, db: Session = Depends(get_db)):
    service = IncidentService(db)
    service.delete(incident_id)
    incidents = service.get_all()
    return templates.TemplateResponse("pages/incidents/table.html", {
        "request": request,
        "incidents": [incident_to_dict(i) for i in incidents],
    })