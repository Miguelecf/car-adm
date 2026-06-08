from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.core.database import engine, Base, ensure_soft_delete_columns
from app.core.config import settings
from app.utils.dates import InvalidDateInput
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

    @app.exception_handler(InvalidDateInput)
    async def invalid_date_handler(request: Request, exc: InvalidDateInput):
        return HTMLResponse(
            f"""
            <div class=\"max-w-2xl rounded-2xl border border-[#F5A623]/30 bg-[#141414] p-8 text-[#F5F0EB]\">
                <h2 class=\"text-3xl font-bold text-[#F5A623]\">Fecha inválida</h2>
                <p class=\"mt-3 text-lg text-[#F5F0EB]\">Revisá el dato ingresado y usá el formato <strong>dd/mm/yyyy</strong>.</p>
                <p class=\"mt-3 text-base text-[#989898]\">{exc}</p>
            </div>
            """,
            status_code=400,
        )

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


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_soft_delete_columns()
