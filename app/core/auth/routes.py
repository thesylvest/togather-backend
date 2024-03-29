from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, status, Request, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.core.auth.utils.contrib import generate_password_reset_token, verify_password_reset_token, authenticate, decode_google_token
from app.core.auth.utils.jwt import create_access_token, create_refresh_token, create_access_token_from_refresh_token
from app.core.auth.schemas import JWTToken, CredentialsSchema, Msg, Token
from app.core.auth.utils.password import get_password_hash
from app.applications.users.utils import update_last_login
from app.applications.users.models import User
import google_auth_oauthlib.flow
from app.settings import config


router = APIRouter()


@router.post("/login/docs/", response_model=JWTToken, tags=["auth"])
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
):
    credentials = CredentialsSchema(username=form_data.username, password=form_data.password)
    user = await authenticate(credentials)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    await update_last_login(user.id)

    refresh_token = create_refresh_token(
        data={"user_id": user.id, "username": user.username, "email": user.email},
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        expires=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "access_token": create_access_token(
            data={"user_id": user.id, "username": user.username, "email": user.email}
        ),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/", response_model=JWTToken, tags=["auth"])
async def login_app(
    response: Response,
    credentials: CredentialsSchema,
):
    user = await authenticate(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    await update_last_login(user.id)

    refresh_token = create_refresh_token(
        data={"user_id": user.id, "username": user.username, "email": user.email},
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        expires=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "access_token": create_access_token(
            data={"user_id": user.id, "username": user.username, "email": user.email}
        ),
        "refresh_token": refresh_token,
        # "refresh_token": create_refresh_token(
        #     data={"user_id": user.id, "username": user.username, "email": user.email},
        # ),
        "token_type": "bearer",
    }


@router.post("/refresh-token/", response_model=JWTToken, tags=["auth"])
async def refresh_token(token: Token, response: Response):
    if token.token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not found",
        )

    access_token, payload = create_access_token_from_refresh_token(token.token)

    new_refresh_token = create_refresh_token(
        data={"user_id": payload["user_id"], "username": payload["username"], "email": payload["email"]}
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        expires=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/password-recovery/{email}/", tags=["auth"], response_model=Msg)
async def recover_password(email: str, background_tasks: BackgroundTasks):
    """
    Password Recovery
    """
    user = await User.get_or_none(email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
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

    user = await User.get_or_none(email=email)
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


@router.post("/register/", response_model=JWTToken, tags=["auth"])
async def register_user(user_in: CredentialsSchema, background_tasks: BackgroundTasks):
    user = await User.get_or_none(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system.",
        )

    user = await User.get_or_none(username=user_in.username)
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

        user_data = {"user_id": created_user.id, "username": created_user.username, "email": created_user.email}
        return {
            "access_token": create_access_token(data=user_data),
            "refresh_token": create_refresh_token(data=user_data),
            "token_type": "bearer",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Error creating user.",
        )


@router.get("/login/google/", tags=["auth"])
async def login_google():
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
        ],
    )

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = "http://localhost:8000/api/auth/login/google/callback"

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )

    return {"url": authorization_url}


@router.get("/login/google/callback/", tags=["auth"])
async def login_google_callback(request: Request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
        ],
    )
    flow.redirect_uri = "http://localhost:8000/api/auth/login/google/callback"

    flow.fetch_token(**dict(request.query_params))

    # Store the credentials in the session.
    # ACTION ITEM for developers:
    #     Store user's access and refresh tokens in your data store if
    #     incorporating this code into your real app.
    credentials = flow.credentials
    decoded_info = decode_google_token(credentials._id_token)
    if decoded_info is None:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    # Process the decoded_info dictionary and return relevant user information
    user = await User.get_or_none(email=decoded_info["email"])

    if user:
        await update_last_login(user.id)
        return {
            "access_token": create_access_token(data={"user_id": user.id}),
            "token_type": "bearer",
        }
    else:
        user_dict = {
            "username": decoded_info["email"].split("@")[
                0
            ],  # TODO: need to check if username already exists
            "email": decoded_info["email"],
            "password": "pass",  # MASSIVE TODO: change this to something more secure
            "first_name": decoded_info["given_name"],  # TODO: change these into proper fields
            "last_name": decoded_info["family_name"],
        }

        hashed_password = get_password_hash(user_dict["password"])
        db_user = CredentialsSchema(**user_dict, password_hash=hashed_password)
        created_user = await User.create(db_user)

    if created_user:
        if config.EMAILS_ENABLED:
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
