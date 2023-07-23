from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, status
from datetime import timedelta

from app.core.auth.utils.contrib import generate_password_reset_token, send_reset_password_email, verify_password_reset_token, authenticate
from app.core.auth.schemas import JWTToken, CredentialsSchema, Msg
from app.core.auth.utils.password import get_password_hash
from app.core.auth.utils.jwt import create_access_token

from app.applications.users.utils import update_last_login
from app.applications.users.models import User

from app.settings import config

router = APIRouter()


@router.post("/access-token", response_model=JWTToken, tags=["login"])
async def login_access_token(credentials: CredentialsSchema):
    pass
    # user = await authenticate(credentials)
    # if user:
    #   await update_last_login(user.id)
    # elif not user:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    # elif not user.is_active:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    # access_token_expires = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    # return {
    #   "access_token": create_access_token(
    #       data={"user_id": user.id}, expires_delta=access_token_expires
    #   ),
    #   "token_type": "bearer",
    # }


@router.post("/password-recovery/{email}", tags=["login"], response_model=Msg)
async def recover_password(email: str, background_tasks: BackgroundTasks):
    """
    Password Recovery
    """
    pass
    # user = await User.get_by_email(email=email)

    # if not user:
    #   raise HTTPException(
    #       status_code=status.HTTP_404_NOT_FOUND,
    #       detail="The user with this username does not exist in the system.",
    #   )
    # password_reset_token = generate_password_reset_token(email=email)
    # background_tasks.add_task(send_reset_password_email, email_to=user.email, email=email, token=password_reset_token)
    # return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", tags=["login"], response_model=Msg)
async def reset_password(token: str = Body(...), new_password: str = Body(...)):
    """
    Reset password
    """
    pass
    # email = verify_password_reset_token(token)
    # if not email:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    # user = await User.get_by_email(email=email)
    # if not user:
    #   raise HTTPException(
    #       status_code=404,
    #       detail="The user with this username does not exist in the system.",
    #   )
    # elif not user.is_active:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    # hashed_password = get_password_hash(new_password)
    # user.hashed_password = hashed_password
    # await user.save()
    # return {"msg": "Password updated successfully"}
