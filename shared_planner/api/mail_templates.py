from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from shared_planner.api.auth import CurrentAdmin
from shared_planner.db.models import MailTemplate, User
from shared_planner.db.session import SessionLock
from shared_planner.mail_render import (
    TEMPLATE_NAMES,
    default_markdown,
)
from shared_planner.mailer_daemon import SUBJECTS

router = APIRouter(
    prefix="/mail_templates",
    tags=["mail_templates"],
    dependencies=[Depends(CurrentAdmin)],
)


class MailTemplateOut(BaseModel):
    name: str
    subject: str
    content: str  # current content (override if any, else default)
    default_content: str
    customized: bool


def _build(name: str, override: MailTemplate | None) -> MailTemplateOut:
    default = default_markdown(name)
    return MailTemplateOut(
        name=name,
        subject=SUBJECTS.get(name, ""),
        content=override.content if override is not None else default,
        default_content=default,
        customized=override is not None,
    )


@router.get("/list")
def list_templates() -> list[MailTemplateOut]:
    with SessionLock() as session:
        result = []
        for name in TEMPLATE_NAMES:
            override = session.get(MailTemplate, name)
            result.append(_build(name, override))
    return result


@router.get("/{name}")
def get_template(name: str) -> MailTemplateOut:
    if name not in TEMPLATE_NAMES:
        raise HTTPException(404, "error.mail_template.not_found")
    with SessionLock() as session:
        override = session.get(MailTemplate, name)
        result = _build(name, override)
    return result


@router.put("/{name}")
def update_template(name: str, content: str = Body(..., embed=True)) -> MailTemplateOut:
    if name not in TEMPLATE_NAMES:
        raise HTTPException(404, "error.mail_template.not_found")
    with SessionLock() as session:
        override = session.get(MailTemplate, name)
        if override is None:
            override = MailTemplate(name=name, content=content)
        else:
            override.content = content
        session.add(override)
        session.commit()
        session.refresh(override)
        result = _build(name, override)
    return result


@router.post("/{name}/reset")
def reset_template(name: str) -> MailTemplateOut:
    """Drop the admin override, reverting to the codebase default."""
    if name not in TEMPLATE_NAMES:
        raise HTTPException(404, "error.mail_template.not_found")
    with SessionLock() as session:
        override = session.get(MailTemplate, name)
        if override is not None:
            session.delete(override)
            session.commit()
        result = _build(name, None)
    return result


@router.post("/{name}/test")
def test_template(
    name: str, admin: User = Depends(CurrentAdmin)
) -> dict:
    if name not in TEMPLATE_NAMES:
        raise HTTPException(404, "error.mail_template.not_found")
    
    from shared_planner.db.models import Notification
    from shared_planner import tz
    from datetime import timedelta
    from shared_planner.db.session import SessionLock
    
    now = tz.now()
    dummy_data = {
        "admin_mail": "admin@example.com",
        "enterprise_message": "Ceci est un message d'entreprise personnalisé.",
        "token": "TEST_TOKEN_12345",
        "validity_hours": 24,
        "email": "nouvel_utilisateur@example.com",
        "group": "Entreprise A",
        "route": "/test/route",
        "user": "Jean Dupont",
        "datetime-start_time": now.strftime("%Y-%m-%d %H:%M"),
        "datetime-previous_start_time": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
        "duration": 120,
        "previous_duration": 60,
        "maps_link": "https://maps.google.com/?q=Paris",
        "shop": "Boutique de Paris",
    }
    
    with SessionLock() as session:
        notification = Notification.create(
            user=admin,
            message=name,
            data=dummy_data,
            mail=True
        )
        session.add(notification)
        session.commit()
        
    return {"status": "queued"}

