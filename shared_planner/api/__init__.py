from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import select

from shared_planner.logs import setup_logging
from shared_planner.db.session import SessionLock
from shared_planner.db.models import Setting

from shared_planner.api.auth import router as auth_router
from shared_planner.api.users import router as users_router
from shared_planner.api.shops import router as shops_router, timerange_router
from shared_planner.api.slots import router as slots_router
from shared_planner.api.reservations import router as reservations_router
from shared_planner.api.settings import router as settings_router
from shared_planner.api.notifications import router as notifications_router
from shared_planner.api.enterprises import router as enterprises_router
from shared_planner.api.documents import router as documents_router
from shared_planner.api.mail_templates import router as mail_templates_router
from shared_planner.api.export import router as export_router


@asynccontextmanager
async def mailer_daemon_context(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    swagger_ui_parameters={"persistAuthorization": True},
    root_path="/api",
    title="Shared Planner API",
    version="1.0",
    lifespan=mailer_daemon_context,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    """Report app health, including whether the database is actually readable.

    A bind-mounted volume can go missing or become unwritable without the
    process crashing, so a plain "is the server up" check isn't enough —
    this does a real read to catch that case too.
    """
    try:
        with SessionLock() as session:
            session.exec(select(Setting).limit(1)).first()
    except Exception:
        raise HTTPException(status_code=503, detail="error.health.db_unavailable")
    return {"status": "healthy"}

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(shops_router)
app.include_router(timerange_router)
app.include_router(slots_router)
app.include_router(reservations_router)
app.include_router(settings_router)
app.include_router(notifications_router)
app.include_router(enterprises_router)
app.include_router(documents_router)
app.include_router(mail_templates_router)
app.include_router(export_router)
