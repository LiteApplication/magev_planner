import re
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import select

from shared_planner.db.models import (
    Enterprise,
    Notification,
    PasswordReset,
    Token,
    User,
)
from shared_planner.db.session import SessionLock
from shared_planner.db.settings import get
from shared_planner.mailer_daemon import send_mail

router = APIRouter(prefix="/auth", tags=["auth"])

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class UserResult(BaseModel):
    """Data model for getting a user profile"""

    id: int
    email: str
    full_name: str
    admin: bool
    group: str = ""
    confirmed: bool = True  # If the user has a password set

    @classmethod
    def from_user(cls, user: User) -> "UserResult":
        return cls(
            email=user.email,
            full_name=user.full_name,
            admin=user.admin,
            id=user.id,
            group=user.group,
            confirmed=user.hashed_password != b"",
        )


def CurrentToken(access_token: Annotated[str, Depends(_oauth2_scheme)]) -> Token:
    """Get the current token from the access token"""
    with SessionLock() as session:
        statement = select(Token).where(Token.access_token == access_token)
        token = session.exec(statement).first()

        if token is None:
            raise HTTPException(status_code=401, detail="error.token.invalid")

        if token.is_expired():
            session.delete(token)
            raise HTTPException(status_code=401, detail="error.token.expired")

        token.renew()
        session.add(token)
        session.commit()
        session.refresh(token)
    return token


def CurrentUser(access_token: Annotated[str, Depends(_oauth2_scheme)]) -> User:
    """Get the current user from the access token"""
    with SessionLock() as session:
        statement = select(Token).where(Token.access_token == access_token)
        token = session.exec(statement).first()

        if token is None:
            raise HTTPException(status_code=401, detail="error.token.invalid")

        if token.is_expired():
            session.delete(token)
            raise HTTPException(status_code=401, detail="error.token.expired")

        token.renew()
        session.add(token)
        session.commit()
        session.refresh(token)
        user = token.user
    return user


def CurrentAdmin(user: Annotated[User, Depends(CurrentUser)]) -> User:
    """Get the current user from the access token"""
    if not user.admin:
        raise HTTPException(status_code=403, detail="error.admin.required")
    return user


@router.get("/me")
def read_users_me(user: Annotated[User, Depends(CurrentUser)]) -> UserResult:
    """Get current user's profile"""
    return UserResult.from_user(user)


@router.post("/login")
def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    with SessionLock() as session:
        credentials.username = credentials.username.strip().lower()

        statement = select(User).where(User.email == credentials.username)
        user = session.exec(statement).first()

        if user is None:
            raise HTTPException(status_code=404, detail="error.auth.user_not_found")
        if not user.check_password(credentials.password):
            raise HTTPException(status_code=401, detail="error.auth.invalid_password")

        token = Token.create_token(user)
        if get("notif_login").asBool():
            session.add(Notification.create(user, "notification.login"))

        session.add(token)
        session.commit()
        session.refresh(token)
    return token


@router.post("/register")
def register(
    email: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
    enterprise: str = Form(...),
    accepted_terms: bool = Form(default=False),
) -> None:
    with SessionLock() as session:
        statement = select(User).where(User.email == email)
        if session.exec(statement).first() is not None:
            raise HTTPException(status_code=409, detail="error.auth.email_exists")

        if len(full_name) < 3:
            raise HTTPException(
                status_code=400, detail="error.auth.full_name_too_short"
            )

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise HTTPException(status_code=400, detail="error.auth.email_invalid")

        # Sanitize inputs to avoid XSS
        full_name = re.sub(r"[^\w\s]", "", full_name).strip()
        email = email.strip().lower()

        enterprise_obj = session.exec(
            select(Enterprise).where(Enterprise.slug == enterprise)
        ).first()
        if enterprise_obj is None:
            raise HTTPException(status_code=400, detail="error.auth.enterprise_invalid")
        if not enterprise_obj.matches_email(email):
            raise HTTPException(status_code=400, detail="error.auth.email_domain_mismatch")
        if enterprise_obj.checkbox_text and not accepted_terms:
            raise HTTPException(status_code=400, detail="error.auth.terms_not_accepted")

        group = enterprise_obj.name

        new_user = User(full_name=full_name, email=email, group=group, admin=False)
        session.add(new_user)

        session.commit()  # Commit to avoid race conditions

        password_token = PasswordReset.create(new_user, session)
        session.add(password_token)

        if get("notif_new_user_created").asBool():
            session.add(
                Notification.create(
                    new_user,
                    "notification.welcome_new_user",
                    {"user": new_user.full_name},
                )
            )

        if get("notif_admin_new_user_created").asBool():
            session.add(
                Notification.create(
                    None,
                    "notification.admin.new_user",
                    {
                        "user": new_user.full_name,
                        "email": new_user.email,
                        "group": new_user.group,
                    },
                    "/admin/users",
                    is_reminder=False,
                    mail=get("email_admin_new_user_created").asBool(),
                )
            )

        session.commit()

        send_mail(
            new_user.full_name,
            new_user.email,
            "first_mail",
            {
                "full_name": new_user.full_name,
                "token": password_token.token,
                "validity_hours": get("reset_token_validity").value,
                "enterprise_message": enterprise_obj.welcome_message,
            },
        )

    return


@router.post("/logout")
def logout(token: Annotated[Token, Depends(CurrentToken)]) -> str:
    with SessionLock() as session:
        token = session.get(Token, token.id)
        session.delete(token)
        session.commit()

    return "Logged out"
