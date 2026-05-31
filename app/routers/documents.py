from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Document, DocumentType
from app.services.document_service import DocumentService
from app.services.vehicle_service import VehicleService
from app.web.templates import templates


router = APIRouter()


def document_to_dict(d: Document) -> dict:
    return {
        "id": d.id,
        "vehicle_id": d.vehicle_id,
        "vehicle_plate": d.vehicle.plate if d.vehicle else "",
        "type": d.type.value if hasattr(d.type, 'value') else d.type,
        "issue_date": d.issue_date.strftime("%Y-%m-%d") if d.issue_date else "",
        "expiry_date": d.expiry_date.strftime("%Y-%m-%d") if d.expiry_date else "",
        "file_notes": d.file_notes or "",
    }


@router.get("/documents", response_class=HTMLResponse)
async def list_documents(request: Request, db: Session = Depends(get_db)):
    service = DocumentService(db)
    documents = service.get_all()
    return templates.TemplateResponse("pages/documents/list.html", {
        "request": request,
        "documents": [document_to_dict(d) for d in documents],
        "current_path": "/documents",
    })


@router.get("/documents/new", response_class=HTMLResponse)
async def new_document_form(request: Request, db: Session = Depends(get_db)):
    vehicle_service = VehicleService(db)
    return templates.TemplateResponse("pages/documents/form.html", {
        "request": request,
        "document": None,
        "vehicles": vehicle_service.get_all(),
        "action": "/documents",
        "current_path": "/documents",
    })


@router.post("/documents")
async def create_document(
    request: Request,
    vehicle_id: int = Form(...),
    type: str = Form(...),
    issue_date: str = Form(...),
    expiry_date: str = Form(...),
    file_notes: str = Form(""),
    db: Session = Depends(get_db),
):
    from datetime import date
    service = DocumentService(db)

    document = service.create({
        "vehicle_id": vehicle_id,
        "type": DocumentType(type),
        "issue_date": date.fromisoformat(issue_date),
        "expiry_date": date.fromisoformat(expiry_date),
        "file_notes": file_notes,
    })
    documents = service.get_all()
    return templates.TemplateResponse("pages/documents/table.html", {
        "request": request,
        "documents": [document_to_dict(d) for d in documents],
    })


@router.delete("/documents/{document_id}")
async def delete_document(request: Request, document_id: int, db: Session = Depends(get_db)):
    service = DocumentService(db)
    service.delete(document_id)
    documents = service.get_all()
    return templates.TemplateResponse("pages/documents/table.html", {
        "request": request,
        "documents": [document_to_dict(d) for d in documents],
    })