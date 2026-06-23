import datetime

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import delete, select
from sqlmodel import or_

from shared_planner.api.auth import CurrentAdmin, CurrentUser
from shared_planner.db.models import Notification, PasswordReset, User, Token, Setting
from shared_planner.db.session import SessionLock
from shared_planner.db.settings import get as get_setting
from shared_planner import tz

router = APIRouter(prefix="/settings", tags=["settings"])


@router.patch("/s/{name}", dependencies=[Depends(CurrentAdmin)])
def patch(name: str, value: str = Body(...)) -> Setting:
    with SessionLock() as session:
        setting = session.get(Setting, name)
        if setting is None:
            raise HTTPException(404, "error.admin.setting_not_found")

        setting.value = value
        session.add(setting)
        session.commit()
        session.refresh(setting)
    return setting


@router.get("/s/{name}")
def get(name: str, user: User = Depends(CurrentUser)) -> Setting:
    with SessionLock() as session:
        setting = session.get(Setting, name)
        if setting is None:
            raise HTTPException(404, "error.admin.setting_not_found")

        if setting.private and not user.admin:
            raise HTTPException(403, "error.admin.required")

    return setting


@router.get("/s/", dependencies=[Depends(CurrentAdmin)])
def list_settings() -> list[Setting]:
    with SessionLock() as session:
        statement = select(Setting)
        settings = session.exec(statement).scalars().all()

    return settings


@router.post("/cleanup_db", dependencies=[Depends(CurrentAdmin)])
def cleanup_db():
    with SessionLock() as session:
        # Clear expired tokens
        query = delete(Token).where(Token.expires_at < tz.now())
        result_auth_token = session.exec(query)

        # Clear password reset tokens
        query = delete(PasswordReset).where(
            or_(
                PasswordReset.expires_at < tz.now(),
                PasswordReset.used == True,  # noqa: E712
            )
        )

        result_password_reset = session.exec(query)

        result_reminders = None
        result_notifications = None
        result_notifications_admin = None

        # Clear expired reminders
        if get_setting("cleanup_reminders_days").asInt() != -1:
            query = delete(Notification).where(
                Notification.date
                < tz.now()
                - datetime.timedelta(
                    days=get_setting("cleanup_reminders_days").asInt()
                ),
                Notification.is_reminder == True,  # noqa: E712
            )
            result_reminders = session.exec(query)

        if get_setting("cleanup_notifications_days").asInt() != -1:
            query = delete(Notification).where(
                Notification.date
                < tz.now()
                - datetime.timedelta(
                    days=get_setting("cleanup_notifications_days").asInt()
                ),
                Notification.user_id != None,  # noqa: E711
            )
            result_notifications = session.exec(query)

        if get_setting("cleanup_notifications_days_admin").asInt() != -1:
            query = delete(Notification).where(
                Notification.date
                < tz.now()
                - datetime.timedelta(
                    days=get_setting("cleanup_notifications_days_admin").asInt()
                ),
                Notification.user_id == None,  # noqa: E711
            )
            result_notifications_admin = session.exec(query)

        session.commit()
    return {
        "message": "success",
        "deleted_tokens": result_auth_token.rowcount,
        "deleted_password_resets": result_password_reset.rowcount,
        "deleted_reminders": result_reminders.rowcount if result_reminders else 0,
        "deleted_notifications": result_notifications.rowcount
        if result_notifications
        else 0,
        "deleted_notifications_admin": result_notifications_admin.rowcount
        if result_notifications_admin
        else 0,
    }
