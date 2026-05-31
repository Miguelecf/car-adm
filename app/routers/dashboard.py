from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.web.templates import templates


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    service = DashboardService(db)

    stats = service.get_stats()
    stats["upcoming_maintenance"] = service.get_upcoming_maintenance()
    stats["upcoming_documents"] = service.get_upcoming_documents()
    stats["profitability"] = service.get_profitability()
    stats["pending_payments"] = service.get_pending_payments()

    return templates.TemplateResponse("pages/dashboard.html", {
        "request": request,
        "stats": stats,
        "current_path": "/",
    })