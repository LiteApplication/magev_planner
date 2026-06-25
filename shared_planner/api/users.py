from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from shared_planner.api.auth import CurrentAdmin, CurrentToken, CurrentUser, UserResult
from shared_planner.db.models import PasswordReset, Token, User
from shared_planner.db.session import SessionLock
from shared_planner.db.settings import get
from shared_planner.mailer_daemon import send_mail

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    """Data model for user creation"""

    email: str
    full_name: str
    phone: str = ""
    password: str
    group: str
    admin: bool = False


@router.post("/create")
def create_user(
    user_data: UserCreate,
    admin: Annotated[User, Depends(CurrentAdmin)],
) -> UserResult:
    """Create a new user"""
    with SessionLock() as session:
        # Check if the user already exists
        statement = select(User).where(User.email == user_data.email)
        user = session.exec(statement).first()
        if user is not None and user.hashed_password:
            raise HTTPException(status_code=400, detail="error.user.already_exists")

        # sanitize user input
        user_data.email = user_data.email.strip()
        user_data.full_name = user_data.full_name.strip()
        user_data.group = user_data.group.strip()

        new_user = User(**user_data.model_dump())
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return UserResult.from_user(new_user)


@router.post("/request_password_reset", dependencies=[Depends(CurrentAdmin)])
def request_password_reset(
    email: dict = Body(examples=[{"email": "test@test.com"}]),
) -> None:
    """Request a password reset for a user"""
    email_address = email.get("email")
    if not email_address:
        raise HTTPException(status_code=400, detail="error.user.email_required")

    with SessionLock() as session:
        statement = select(User).where(User.email == email_address)
        user = session.exec(statement).first()
        if user is None:
            return  # Do not raise an error to prevent email enumeration

        # Create a new password reset request
        reset = PasswordReset.create(user, session)
        session.add(reset)
        session.commit()

        # Send the email
        send_mail(
            user.full_name,
            user.email,
            "password_reset",
            {"token": reset.token, "validity_hours": get("reset_token_validity").value},
        )
    return


@router.post("/reset_password")
def reset_password(
    token: str = Body(...),
    password: str = Body(...),
) -> None:
    """Reset a user's password"""
    with SessionLock() as session:
        reset = PasswordReset.check_token(token, session)

        if len(password) < 8:
            raise HTTPException(status_code=400, detail="error.auth.password_too_short")

        # Reset the user's password
        user = reset.user
        user.set_password(password)
        session.add(user)
        session.delete(reset)
        session.commit()
    return


@router.get("/list", dependencies=[Depends(CurrentAdmin)])
def list_users() -> list[UserResult]:
    """List all users"""
    with SessionLock() as session:
        statement = select(User)
        users = session.exec(statement).all()
        users = [UserResult.from_user(user) for user in users]
    return users


@router.get("/get/{user_id}", dependencies=[Depends(CurrentAdmin)])
def get_user(
    user_id: int,
) -> UserResult:
    """Get a specific user"""
    with SessionLock() as session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        if user is None:
            raise HTTPException(status_code=404, detail="error.user.not_found")
    return UserResult.from_user(user)


@router.delete("/delete/{user_id}", dependencies=[Depends(CurrentAdmin)])
def delete_user(user_id: int) -> UserResult:
    """Delete a specific user"""
    with SessionLock() as session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        if user is None:
            raise HTTPException(status_code=404, detail="error.user.not_found")
        session.delete(user)
        session.commit()
        result = UserResult.from_user(user)
    return result


@router.put("/update")
def update_user(
    user_data: UserResult, exec_user: User = Depends(CurrentAdmin)
) -> UserResult:
    """Update a specific user"""
    with SessionLock() as session:
        statement = select(User).where(User.id == user_data.id)
        user = session.exec(statement).first()
        if user is None:
            raise HTTPException(status_code=404, detail="error.user.not_found")
        user.email = user_data.email
        user.full_name = user_data.full_name
        if user_data.id == exec_user.id:
            if user_data.admin != exec_user.admin:
                raise HTTPException(
                    status_code=400, detail="error.user.cant_set_self_admin"
                )
        user.admin = user_data.admin
        user.full_name = user_data.full_name
        user.email = user_data.email
        user.phone = user_data.phone
        user.group = user_data.group

        session.add(user)
        session.commit()
        session.refresh(user)
    return UserResult.from_user(user)


@router.put("/me")
def update_me(
    current_password: Annotated[str, Body()],
    user_data: UserCreate,
    token: Annotated[Token, Depends(CurrentToken)],
) -> UserResult:
    """Update the current user"""
    with SessionLock() as session:
        statement = select(User).where(User.id == token.user_id)
        user = session.exec(statement).first()
        if user is None:
            raise HTTPException(status_code=404, detail="error.user.not_found")

        # Check that the current password is correct
        if not user.check_password(current_password):
            raise HTTPException(status_code=401, detail="error.auth.invalid_password")

        # Check that the email is the same
        if user.email != user_data.email:
            raise HTTPException(status_code=400, detail="error.user.email_not_same")

        user.full_name = user_data.full_name
        user.set_password(user_data.password)
        session.add(user)
        session.commit()
        session.refresh(user)
    return UserResult.from_user(user)


@router.get("/me")
def read_users_me(user: Annotated[User, Depends(CurrentUser)]) -> UserResult:
    """Get current user's profile"""
    return UserResult.from_user(user)
