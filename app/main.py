from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.database import engine, Base
from app.core.config import settings
import app.models as models

from app.routers.dashboard import router as dashboard_router
from app.routers.vehicles import router as vehicles_router
from app.routers.drivers import router as drivers_router
from app.routers.contracts import router as contracts_router
from app.routers.payments import router as payments_router
from app.routers.maintenance import router as maintenance_router
from app.routers.documents import router as documents_router
from app.routers.incidents import router as incidents_router
from app.routers.settings import router as settings_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

    app.include_router(dashboard_router)
    app.include_router(vehicles_router, tags=["vehicles"])
    app.include_router(drivers_router, tags=["drivers"])
    app.include_router(contracts_router, tags=["contracts"])
    app.include_router(payments_router, tags=["payments"])
    app.include_router(maintenance_router, tags=["maintenance"])
    app.include_router(documents_router, tags=["documents"])
    app.include_router(incidents_router, tags=["incidents"])
    app.include_router(settings_router, tags=["settings"])

    return app


app = create_app()


@app.get("/", response_class=HTMLResponse)
async def root():
    from app.web.templates import templates
    return templates.TemplateResponse("pages/dashboard.html", {"request": {}})


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)