from datetime import date
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Vehicle, VehicleStatus
from app.services.vehicle_service import VehicleService
from app.web.templates import templates


router = APIRouter()


def vehicle_to_dict(v: Vehicle) -> dict:
    return {
        "id": v.id,
        "brand": v.brand,
        "model": v.model,
        "year": v.year,
        "plate": v.plate,
        "color": v.color,
        "current_km": v.current_km,
        "status": v.status.value if hasattr(v.status, 'value') else v.status,
        "created_at": v.created_at.strftime("%d/%m/%Y") if v.created_at else "",
    }


@router.get("/vehicles", response_class=HTMLResponse)
async def list_vehicles(request: Request, db: Session = Depends(get_db)):
    service = VehicleService(db)
    vehicles = service.get_all()
    return templates.TemplateResponse(request, "pages/vehicles/list.html", {
        "vehicles": [vehicle_to_dict(v) for v in vehicles],
        "current_path": "/vehicles",
    })


@router.get("/vehicles/new", response_class=HTMLResponse)
async def new_vehicle_form(request: Request):
    return templates.TemplateResponse(request, "pages/vehicles/form.html", {
        "vehicle": None,
        "action": "/vehicles",
        "current_path": "/vehicles",
    })


@router.post("/vehicles")
async def create_vehicle(
    request: Request,
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    plate: str = Form(...),
    color: str = Form(""),
    current_km: int = Form(0),
    db: Session = Depends(get_db),
):
    service = VehicleService(db)
    vehicle = service.create({
        "brand": brand,
        "model": model,
        "year": year,
        "plate": plate,
        "color": color,
        "current_km": current_km,
        "status": VehicleStatus.ACTIVO,
    })
    vehicles = service.get_all()
    return templates.TemplateResponse(request, "pages/vehicles/table.html", {
        "vehicles": [vehicle_to_dict(v) for v in vehicles],
    })


@router.get("/vehicles/{vehicle_id}/edit", response_class=HTMLResponse)
async def edit_vehicle_form(request: Request, vehicle_id: int, db: Session = Depends(get_db)):
    service = VehicleService(db)
    vehicle = service.get_by_id(vehicle_id)
    if not vehicle:
        return HTMLResponse("No encontrado", status_code=404)
    return templates.TemplateResponse(request, "pages/vehicles/form.html", {
        "vehicle": vehicle_to_dict(vehicle),
        "action": f"/vehicles/{vehicle_id}",
        "current_path": "/vehicles",
    })


@router.post("/vehicles/{vehicle_id}")
async def update_vehicle(
    request: Request,
    vehicle_id: int,
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    plate: str = Form(...),
    color: str = Form(""),
    current_km: int = Form(0),
    status: str = Form("activo"),
    db: Session = Depends(get_db),
):
    service = VehicleService(db)
    vehicle = service.update(vehicle_id, {
        "brand": brand,
        "model": model,
        "year": year,
        "plate": plate,
        "color": color,
        "current_km": current_km,
        "status": VehicleStatus(status),
    })
    vehicles = service.get_all()
    return templates.TemplateResponse(request, "pages/vehicles/table.html", {
        "vehicles": [vehicle_to_dict(v) for v in vehicles],
    })


@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(request: Request, vehicle_id: int, db: Session = Depends(get_db)):
    service = VehicleService(db)
    service.delete(vehicle_id)
    vehicles = service.get_all()
    return templates.TemplateResponse(request, "pages/vehicles/table.html", {
        "vehicles": [vehicle_to_dict(v) for v in vehicles],
    })