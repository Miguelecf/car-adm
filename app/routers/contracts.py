from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Contract, ContractStatus
from app.services.contract_service import ContractService
from app.services.vehicle_service import VehicleService
from app.services.driver_service import DriverService
from app.utils.dates import parse_latam_date
from app.web.templates import templates


router = APIRouter()


def contract_to_dict(c: Contract) -> dict:
    return {
        "id": c.id,
        "vehicle_id": c.vehicle_id,
        "driver_id": c.driver_id,
        "vehicle_plate": c.vehicle.plate if c.vehicle else "",
        "driver_name": c.driver.name if c.driver else "",
        "start_date": c.start_date.strftime("%Y-%m-%d") if c.start_date else "",
        "end_date": c.end_date.strftime("%Y-%m-%d") if c.end_date else "",
        "weekly_amount": c.weekly_amount,
        "deposit_amount": c.deposit_amount,
        "start_km": c.start_km,
        "end_km": c.end_km,
        "status": c.status.value if hasattr(c.status, 'value') else c.status,
    }


@router.get("/contracts", response_class=HTMLResponse)
async def list_contracts(request: Request, db: Session = Depends(get_db)):
    service = ContractService(db)
    contracts = service.get_all()
    return templates.TemplateResponse(request, "pages/contracts/list.html", {
        "contracts": [contract_to_dict(c) for c in contracts],
        "current_path": "/contracts",
    })


@router.get("/contracts/new", response_class=HTMLResponse)
async def new_contract_form(request: Request, db: Session = Depends(get_db)):
    vehicle_service = VehicleService(db)
    driver_service = DriverService(db)
    return templates.TemplateResponse(request, "pages/contracts/form.html", {
        "contract": None,
        "vehicles": vehicle_service.get_all(),
        "drivers": driver_service.get_all(),
        "action": "/contracts",
        "current_path": "/contracts",
    })


@router.post("/contracts")
async def create_contract(
    request: Request,
    vehicle_id: int = Form(...),
    driver_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(""),
    weekly_amount: int = Form(...),
    deposit_amount: int = Form(0),
    start_km: int = Form(...),
    db: Session = Depends(get_db),
):
    service = ContractService(db)

    contract = service.create({
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "start_date": parse_latam_date(start_date, "Fecha inicio"),
        "end_date": parse_latam_date(end_date, "Fecha fin", required=False),
        "weekly_amount": weekly_amount,
        "deposit_amount": deposit_amount,
        "start_km": start_km,
        "status": ContractStatus.ACTIVO,
    })
    contracts = service.get_all()
    return templates.TemplateResponse(request, "pages/contracts/list.html", {
        "contracts": [contract_to_dict(c) for c in contracts],
        "current_path": "/contracts",
    })


@router.get("/contracts/{contract_id}/edit", response_class=HTMLResponse)
async def edit_contract_form(request: Request, contract_id: int, db: Session = Depends(get_db)):
    service = ContractService(db)
    contract = service.get_by_id(contract_id)
    if not contract:
        return HTMLResponse("No encontrado", status_code=404)
    vehicle_service = VehicleService(db)
    driver_service = DriverService(db)
    return templates.TemplateResponse(request, "pages/contracts/form.html", {
        "contract": contract_to_dict(contract),
        "vehicles": vehicle_service.get_all(),
        "drivers": driver_service.get_all(),
        "action": f"/contracts/{contract_id}",
        "current_path": "/contracts",
    })


@router.post("/contracts/{contract_id}")
async def update_contract(
    request: Request,
    contract_id: int,
    vehicle_id: int = Form(...),
    driver_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(""),
    weekly_amount: int = Form(...),
    deposit_amount: int = Form(0),
    start_km: int = Form(...),
    end_km: int = Form(0),
    status: str = Form("activo"),
    db: Session = Depends(get_db),
):
    service = ContractService(db)

    contract = service.update(contract_id, {
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "start_date": parse_latam_date(start_date, "Fecha inicio"),
        "end_date": parse_latam_date(end_date, "Fecha fin", required=False),
        "weekly_amount": weekly_amount,
        "deposit_amount": deposit_amount,
        "start_km": start_km,
        "end_km": end_km if end_km else None,
        "status": ContractStatus(status),
    })
    contracts = service.get_all()
    return templates.TemplateResponse(request, "pages/contracts/list.html", {
        "contracts": [contract_to_dict(c) for c in contracts],
        "current_path": "/contracts",
    })


@router.delete("/contracts/{contract_id}")
async def delete_contract(request: Request, contract_id: int, db: Session = Depends(get_db)):
    service = ContractService(db)
    service.delete(contract_id)
    contracts = service.get_all()
    return templates.TemplateResponse(request, "pages/contracts/table.html", {
        "contracts": [contract_to_dict(c) for c in contracts],
    })
