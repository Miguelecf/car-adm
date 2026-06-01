from datetime import date
from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates
from app.core.config import settings


templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)

templates.env.globals["settings"] = settings
templates.env.globals["TODAY"] = date.today()