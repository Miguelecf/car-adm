from datetime import date, datetime
from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates
from app.core.config import settings


templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)

templates.env.globals["settings"] = settings
templates.env.globals["TODAY"] = date.today()


def _format_date_latam(value):
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            dt = date.fromisoformat(value)
        except ValueError:
            return value
        return dt.strftime("%d/%m/%Y")
    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")
    return str(value)


templates.env.filters["format_date_latam"] = _format_date_latam