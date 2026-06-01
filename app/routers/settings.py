from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from app.web.templates import templates
from app.core.config import settings


router = APIRouter()


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(request, "pages/settings.html", {
        "current_path": "/settings",
        "payment_day": settings.PAYMENT_DAY,
    })


@router.post("/settings")
async def update_settings(
    request: Request,
    payment_day: int = Form(...),
):
    from app.core.config import Settings
    s = Settings()
    s.PAYMENT_DAY = payment_day
    return templates.TemplateResponse(request, "pages/settings.html", {
        "current_path": "/settings",
        "payment_day": payment_day,
        "success": True,
    })