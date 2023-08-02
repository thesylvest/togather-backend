from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, status

from app.core.auth.utils.contrib import (
    generate_password_reset_token,
    verify_password_reset_token,
    authenticate,
)
from app.core.auth.schemas import JWTToken, CredentialsSchema, Msg
from app.core.auth.utils.password import get_password_hash
from app.core.auth.utils.jwt import create_access_token

from app.applications.users.utils import update_last_login
from app.applications.users.models import User
from app.settings import config


router = APIRouter()


@router.post("/access-token", response_model=JWTToken, tags=["auth"])
async def login_access_token(credentials: CredentialsSchema):
    user = await authenticate(credentials)
    if user:
        await update_last_login(user.id)
    elif not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect credentials",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return {
        "access_token": create_access_token(
            data={"user_id": user.id},
        ),
        "token_type": "bearer",
    }


@router.post("/password-recovery/{email}", tags=["auth"], response_model=Msg)
async def recover_password(email: str, background_tasks: BackgroundTasks):
    """
    Password Recovery
    """
    user = await User.get_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    if config.EMAILS_ENABLED:
        background_tasks.add_task(
            send_reset_password_email,
            email_to=user.email,
            email=email,
            token=password_reset_token,
        )
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", tags=["auth"], response_model=Msg)
async def reset_password(token: str = Body(...), new_password: str = Body(...)):
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    user = await User.get_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    hashed_password = get_password_hash(new_password)
    user.password_hash = hashed_password
    await user.save()
    return {"msg": "Password updated successfully"}


@router.post("/register", response_model=JWTToken, tags=["auth"])
async def register_user(user_in: CredentialsSchema, background_tasks: BackgroundTasks):
    user = await User.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system.",
        )

    user = await User.get_by_username(username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists in the system.",
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = CredentialsSchema(**user_in.to_dict(), password_hash=hashed_password)
    created_user = await User.create(db_user)

    if created_user:
        if config.EMAILS_ENABLED and user_in.email:
            background_tasks.add_task(
                send_new_account_email,
                email_to=user_in.email,
                username=user_in.email,
                password=user_in.password,
            )

        return {
            "access_token": create_access_token(data={"user_id": created_user.id}),
            "token_type": "bearer",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Error creating user.",
        )
