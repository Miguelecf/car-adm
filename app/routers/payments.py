from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Payment, PaymentStatus, PaymentMethod
from app.services.payment_service import PaymentService
from app.services.contract_service import ContractService
from app.utils.dates import parse_latam_date
from app.web.templates import templates


router = APIRouter()


def payment_to_dict(p: Payment) -> dict:
    return {
        "id": p.id,
        "contract_id": p.contract_id,
        "amount": p.amount,
        "due_date": p.due_date.strftime("%d/%m/%Y") if p.due_date else "",
        "payment_date": p.payment_date.strftime("%d/%m/%Y") if p.payment_date else "",
        "method": p.method.value if p.method else "",
        "status": p.status.value if hasattr(p.status, 'value') else p.status,
        "notes": p.notes or "",
        "driver_name": p.contract.driver.name if p.contract and p.contract.driver else "",
        "vehicle_plate": p.contract.vehicle.plate if p.contract and p.contract.vehicle else "",
    }


@router.get("/payments", response_class=HTMLResponse)
async def list_payments(request: Request, db: Session = Depends(get_db)):
    service = PaymentService(db)
    payments = service.get_all()
    return templates.TemplateResponse(request, "pages/payments/list.html", {
        "payments": [payment_to_dict(p) for p in payments],
        "current_path": "/payments",
    })


@router.get("/payments/new", response_class=HTMLResponse)
async def new_payment_form(request: Request, db: Session = Depends(get_db)):
    contract_service = ContractService(db)
    return templates.TemplateResponse(request, "pages/payments/form.html", {
        "payment": None,
        "contracts": contract_service.get_active(),
        "action": "/payments",
        "current_path": "/payments",
    })


@router.post("/payments")
async def create_payment(
    request: Request,
    contract_id: int = Form(...),
    amount: int = Form(...),
    due_date: str = Form(...),
    method: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    service = PaymentService(db)

    payment = service.create({
        "contract_id": contract_id,
        "amount": amount,
        "due_date": parse_latam_date(due_date, "Fecha límite"),
        "method": PaymentMethod(method) if method else None,
        "notes": notes,
        "status": PaymentStatus.PENDIENTE,
    })
    payments = service.get_all()
    return templates.TemplateResponse(request, "pages/payments/list.html", {
        "payments": [payment_to_dict(p) for p in payments],
        "current_path": "/payments",
    })


@router.post("/payments/{payment_id}/mark-paid")
async def mark_payment_paid(
    request: Request,
    payment_id: int,
    payment_date: str = Form(...),
    method: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    service = PaymentService(db)
    service.mark_paid(payment_id, parse_latam_date(payment_date, "Fecha de pago"), PaymentMethod(method), notes)
    payments = service.get_all()
    return templates.TemplateResponse(request, "pages/payments/table.html", {
        "payments": [payment_to_dict(p) for p in payments],
    })


@router.get("/payments/{payment_id}/pay", response_class=HTMLResponse)
async def pay_payment_form(request: Request, payment_id: int):
    from datetime import date
    return templates.TemplateResponse(request, "pages/payments/pay_form.html", {
        "payment_id": payment_id,
        "today": date.today().strftime("%d/%m/%Y"),
        "current_path": "/payments",
    })


@router.delete("/payments/{payment_id}")
async def delete_payment(request: Request, payment_id: int, db: Session = Depends(get_db)):
    service = PaymentService(db)
    service.delete(payment_id)
    payments = service.get_all()
    return templates.TemplateResponse(request, "pages/payments/table.html", {
        "payments": [payment_to_dict(p) for p in payments],
    })


@router.post("/payments/generate")
async def generate_payments(request: Request, db: Session = Depends(get_db)):
    service = PaymentService(db)
    service.generate_weekly_payments()
    payments = service.get_all()
    return templates.TemplateResponse(request, "pages/payments/table.html", {
        "payments": [payment_to_dict(p) for p in payments],
    })
