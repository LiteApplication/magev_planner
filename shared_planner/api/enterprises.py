import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from shared_planner.api.auth import CurrentAdmin
from shared_planner.db.models import Enterprise
from shared_planner.db.session import SessionLock

router = APIRouter(prefix="/enterprises", tags=["enterprises"])


# Initial enterprises seeded when the table is empty (previously hardcoded in the UI).
DEFAULT_ENTERPRISES = [
    "MAGEV",
    "TOTAL",
    "ADA",
    "CBRE",
    "SalesForce",
    "ABEILLE",
    "Diffuz",
    "France Bénévolat",
    "Bénévolt",
]


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w]+", "-", value, flags=re.UNICODE)
    return value.strip("-")


def ensure_default_enterprises():
    """Seed the default enterprises once, if none exist yet."""
    with SessionLock() as session:
        if session.exec(select(Enterprise)).first() is not None:
            return
        for name in DEFAULT_ENTERPRISES:
            session.add(Enterprise(slug=slugify(name), name=name))
        session.commit()


class EnterprisePublic(BaseModel):
    """Fields exposed to the (unauthenticated) registration form."""

    slug: str
    name: str
    email_domains: str
    checkbox_text: str

    @classmethod
    def from_enterprise(cls, e: Enterprise) -> "EnterprisePublic":
        return cls(
            slug=e.slug,
            name=e.name,
            email_domains=e.email_domains,
            checkbox_text=e.checkbox_text,
        )


class EnterpriseIn(BaseModel):
    slug: str
    name: str
    email_domains: str = ""
    checkbox_text: str = ""
    welcome_message: str = ""
    reminder_message: str = ""


@router.get("/public")
def list_public() -> list[EnterprisePublic]:
    """List enterprises for the registration form (no private message fields)."""
    with SessionLock() as session:
        enterprises = session.exec(select(Enterprise)).all()
        result = [EnterprisePublic.from_enterprise(e) for e in enterprises]
    return result


@router.get("/list", dependencies=[Depends(CurrentAdmin)])
def list_enterprises() -> list[Enterprise]:
    with SessionLock() as session:
        result = session.exec(select(Enterprise)).all()
    return result


@router.post("/create", dependencies=[Depends(CurrentAdmin)])
def create_enterprise(data: EnterpriseIn) -> Enterprise:
    with SessionLock() as session:
        slug = slugify(data.slug or data.name)
        if not slug:
            raise HTTPException(400, "error.enterprise.invalid_slug")
        if _slug_taken(session, slug):
            raise HTTPException(409, "error.enterprise.slug_exists")
        enterprise = Enterprise(
            slug=slug,
            name=data.name.strip(),
            email_domains=data.email_domains,
            checkbox_text=data.checkbox_text,
            welcome_message=data.welcome_message,
            reminder_message=data.reminder_message,
        )
        session.add(enterprise)
        session.commit()
        session.refresh(enterprise)
    return enterprise


@router.put("/{enterprise_id}/update", dependencies=[Depends(CurrentAdmin)])
def update_enterprise(enterprise_id: int, data: EnterpriseIn) -> Enterprise:
    with SessionLock() as session:
        enterprise = session.get(Enterprise, enterprise_id)
        if enterprise is None:
            raise HTTPException(404, "error.enterprise.not_found")
        slug = slugify(data.slug or data.name)
        if not slug:
            raise HTTPException(400, "error.enterprise.invalid_slug")
        if slug != enterprise.slug and _slug_taken(session, slug):
            raise HTTPException(409, "error.enterprise.slug_exists")
        enterprise.slug = slug
        enterprise.name = data.name.strip()
        enterprise.email_domains = data.email_domains
        enterprise.checkbox_text = data.checkbox_text
        enterprise.welcome_message = data.welcome_message
        enterprise.reminder_message = data.reminder_message
        session.add(enterprise)
        session.commit()
        session.refresh(enterprise)
    return enterprise


@router.delete("/{enterprise_id}/delete", dependencies=[Depends(CurrentAdmin)])
def delete_enterprise(enterprise_id: int) -> None:
    with SessionLock() as session:
        enterprise = session.get(Enterprise, enterprise_id)
        if enterprise is None:
            raise HTTPException(404, "error.enterprise.not_found")
        session.delete(enterprise)
        session.commit()


def _slug_taken(session, slug: str) -> bool:
    return session.exec(select(Enterprise).where(Enterprise.slug == slug)).first() is not None
