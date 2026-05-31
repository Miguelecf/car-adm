from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Driver
from app.services.driver_service import DriverService
from app.web.templates import templates


router = APIRouter()


def driver_to_dict(d: Driver) -> dict:
    return {
        "id": d.id,
        "name": d.name,
        "dni": d.dni,
        "phone": d.phone or "",
        "address": d.address or "",
        "license_number": d.license_number or "",
        "license_expiry": d.license_expiry.strftime("%Y-%m-%d") if d.license_expiry else "",
    }


@router.get("/drivers", response_class=HTMLResponse)
async def list_drivers(request: Request, db: Session = Depends(get_db)):
    service = DriverService(db)
    drivers = service.get_all()
    return templates.TemplateResponse("pages/drivers/list.html", {
        "request": request,
        "drivers": [driver_to_dict(d) for d in drivers],
        "current_path": "/drivers",
    })


@router.get("/drivers/new", response_class=HTMLResponse)
async def new_driver_form(request: Request):
    return templates.TemplateResponse("pages/drivers/form.html", {
        "request": request,
        "driver": None,
        "action": "/drivers",
        "current_path": "/drivers",
    })


@router.post("/drivers")
async def create_driver(
    request: Request,
    name: str = Form(...),
    dni: str = Form(...),
    phone: str = Form(""),
    address: str = Form(""),
    license_number: str = Form(""),
    license_expiry: str = Form(""),
    db: Session = Depends(get_db),
):
    from datetime import date
    service = DriverService(db)

    license_expiry_date = None
    if license_expiry:
        license_expiry_date = date.fromisoformat(license_expiry)

    driver = service.create({
        "name": name,
        "dni": dni,
        "phone": phone,
        "address": address,
        "license_number": license_number,
        "license_expiry": license_expiry_date,
    })
    drivers = service.get_all()
    return templates.TemplateResponse("pages/drivers/table.html", {
        "request": request,
        "drivers": [driver_to_dict(d) for d in drivers],
    })


@router.get("/drivers/{driver_id}/edit", response_class=HTMLResponse)
async def edit_driver_form(request: Request, driver_id: int, db: Session = Depends(get_db)):
    service = DriverService(db)
    driver = service.get_by_id(driver_id)
    if not driver:
        return HTMLResponse("No encontrado", status_code=404)
    return templates.TemplateResponse("pages/drivers/form.html", {
        "request": request,
        "driver": driver_to_dict(driver),
        "action": f"/drivers/{driver_id}",
        "current_path": "/drivers",
    })


@router.post("/drivers/{driver_id}")
async def update_driver(
    request: Request,
    driver_id: int,
    name: str = Form(...),
    dni: str = Form(...),
    phone: str = Form(""),
    address: str = Form(""),
    license_number: str = Form(""),
    license_expiry: str = Form(""),
    db: Session = Depends(get_db),
):
    from datetime import date
    service = DriverService(db)

    license_expiry_date = None
    if license_expiry:
        license_expiry_date = date.fromisoformat(license_expiry)

    driver = service.update(driver_id, {
        "name": name,
        "dni": dni,
        "phone": phone,
        "address": address,
        "license_number": license_number,
        "license_expiry": license_expiry_date,
    })
    drivers = service.get_all()
    return templates.TemplateResponse("pages/drivers/table.html", {
        "request": request,
        "drivers": [driver_to_dict(d) for d in drivers],
    })


@router.delete("/drivers/{driver_id}")
async def delete_driver(request: Request, driver_id: int, db: Session = Depends(get_db)):
    service = DriverService(db)
    service.delete(driver_id)
    drivers = service.get_all()
    return templates.TemplateResponse("pages/drivers/table.html", {
        "request": request,
        "drivers": [driver_to_dict(d) for d in drivers],
    })