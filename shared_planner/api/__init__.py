from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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
