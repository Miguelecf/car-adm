from datetime import date
from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates
from app.core.config import settings


templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)


def add_template_functions(request: Request, call_next):
    async def wrapper(*args, **kwargs):
        response = await call_next(*args, **kwargs)
        return response

    async def template_response(name, context):
        context["settings"] = settings
        context["current_path"] = getattr(request, "scope", {}).get("path", "/")
        return templates.TemplateResponse(name, context)

    return template_response


templates.env.globals["settings"] = settings
templates.env.globals["TODAY"] = date.today()