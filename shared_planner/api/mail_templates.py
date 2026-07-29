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
    subject: str  # current subject (override if set, else default)
    default_subject: str
    content: str  # current content (override if any, else default)
    default_content: str
    customized: bool


def _build(name: str, override: MailTemplate | None) -> MailTemplateOut:
    default = default_markdown(name)
    default_subject = SUBJECTS.get(name, "")
    return MailTemplateOut(
        name=name,
        subject=(override.subject if override is not None and override.subject else default_subject),
        default_subject=default_subject,
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
def update_template(
    name: str,
    content: str = Body(..., embed=True),
    subject: str = Body("", embed=True),
) -> MailTemplateOut:
    if name not in TEMPLATE_NAMES:
        raise HTTPException(404, "error.mail_template.not_found")
    # An empty subject means "use the codebase default", so don't store it as an
    # override of the default value.
    if subject.strip() == SUBJECTS.get(name, ""):
        subject = ""
    with SessionLock() as session:
        override = session.get(MailTemplate, name)
        if override is None:
            override = MailTemplate(name=name, content=content, subject=subject)
        else:
            override.content = content
            override.subject = subject
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


def _dummy_data() -> dict:
    """Representative sample values used when previewing/testing a template."""
    from shared_planner import tz
    from datetime import timedelta

    now = tz.now()
    return {
        "admin_mail": "admin@example.com",
        "enterprise_message": "Ceci est un message d'entreprise personnalisé.",
        "token": "TEST_TOKEN_12345",
        "validity_hours": 24,
        "email": "nouvel_utilisateur@example.com",
        "group": "Entreprise A",
        "route": "/test/route",
        "user": "Jean Dupont",
        "full_name": "Jean Dupont",
        "datetime-start_time": now.strftime("%Y-%m-%d %H:%M"),
        "datetime-previous_start_time": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
        "duration": 120,
        "previous_duration": 60,
        "maps_link": "https://maps.google.com/?q=Paris",
        "shop": "Boutique de Paris",
    }


@router.post("/{name}/test")
def test_template(name: str, admin: User = Depends(CurrentAdmin)) -> dict:
    """Queue a test mail rendered from the currently saved template."""
    if name not in TEMPLATE_NAMES:
        raise HTTPException(404, "error.mail_template.not_found")

    from shared_planner.db.models import Notification

    with SessionLock() as session:
        notification = Notification.create(
            user=admin, message=name, data=_dummy_data(), mail=True
        )
        session.add(notification)
        session.commit()

    return {"status": "queued"}


@router.post("/{name}/test_draft")
def test_draft_template(
    name: str,
    content: str = Body(..., embed=True),
    subject: str = Body("", embed=True),
    admin: User = Depends(CurrentAdmin),
) -> dict:
    """Send a test mail rendered from an unsaved draft (content + subject).

    The draft is not persisted; it is rendered on the fly and sent to the
    requesting admin so a template can be previewed before saving it.
    """
    if name not in TEMPLATE_NAMES:
        raise HTTPException(404, "error.mail_template.not_found")

    from shared_planner.mailer_daemon import send_rendered_mail

    subject = subject.strip() or SUBJECTS.get(name, "Notification")
    send_rendered_mail(admin.full_name, admin.email, subject, content, _dummy_data())
    return {"status": "sent"}

