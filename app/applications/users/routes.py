from fastapi import BackgroundTasks, APIRouter, Depends, HTTPException, Request, Query
from typing import List

from app.core.auth.utils.contrib import (
    get_current_active_superuser,
    get_current_active_user,
)
from app.core.auth.utils.password import get_password_hash
from app.core.base.paginator import paginate
from .schemas import BaseUserOut, BaseUserCreate, BaseUserUpdate
from app.applications.events.schemas import BaseEventOut
from .models import User, Connection
from app.settings import config

router = APIRouter()


@router.get("/", status_code=200, tags=["users"])
async def read_users(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Retrieve users.
    """
    users = User.all()
    return await paginate(users, page, page_size, request, BaseUserOut, None)


@router.post("/", response_model=BaseUserOut, status_code=201, tags=["users"])
async def create_user(
    *,
    user_in: BaseUserCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Create new user.
    """
    user = await User.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system.",
        )

    if user_in.username:
        user = await User.get_by_username(username=user_in.username)
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists in the system.",
            )

    hashed_password = get_password_hash(user_in.password)
    db_user = BaseUserCreate(
        **user_in.create_update_dict(), password_hash=hashed_password
    )
    created_user = await User.create(db_user)

    if config.EMAILS_ENABLED and user_in.email:
        background_tasks.add_task(
            send_new_account_email,
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
        )
    return created_user


@router.put("/me", response_model=BaseUserOut, status_code=200, tags=["users"])
async def update_user_me(
    user_in: BaseUserUpdate, current_user: User = Depends(get_current_active_user)
):
    """
    Update own user.
    """
    user = current_user

    for field, value in user_in.create_update_dict().items():
        if value is not None:
            setattr(user, field, value)

    await user.save()
    return user


@router.get("/me", response_model=BaseUserOut, status_code=200, tags=["users"])
def read_user_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's info.
    """
    user_out = BaseUserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        bio=current_user.bio,
        gender=current_user.gender,
        social_links=current_user.social_links,
        birth_date=current_user.birth_date,
    )
    return user_out


@router.get("/{user_id}", response_model=BaseUserOut, status_code=200, tags=["users"])
async def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific user's info by username.
    """
    user = await User.get_or_none(id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=BaseUserOut, status_code=200, tags=["users"])
async def update_user(
    user_id: int,
    user_in: BaseUserUpdate,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Update a user.
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await user.update_from_dict(user_in.create_update_dict_superuser())
    await user.save()
    return user


@router.get(
    "/{user_id}/connections",
    response_model=List[BaseUserOut],
    status_code=200,
    tags=["users"],
)
async def get_user_connections(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific user's connections by username.
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )

    await user.fetch_related("sent_connections", "received_connections")
    sent = await user.sent_connections.filter(is_accepted=True).prefetch_related(
        "to_user"
    )
    received = await user.received_connections.filter(
        is_accepted=True
    ).prefetch_related("from_user")

    out = []
    for connection in sent:
        out.append(
            BaseUserOut(
                id=connection.to_user.id,
                username=connection.to_user.username,
                email=connection.to_user.email,
                created_at=connection.to_user.created_at,
                first_name=connection.to_user.first_name,
                last_name=connection.to_user.last_name,
            )
        )
    for connection in received:
        out.append(
            BaseUserOut(
                id=connection.from_user.id,
                username=connection.from_user.username,
                email=connection.from_user.email,
                created_at=connection.from_user.created_at,
                first_name=connection.from_user.first_name,
                last_name=connection.from_user.last_name,
            )
        )

    return out


@router.get(
    "/me/connections/received",
    response_model=List[BaseUserOut],
    status_code=200,
    tags=["users"],
)
async def get_user_received_connections(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's waiting received connections
    """

    await current_user.fetch_related("received_connections")
    received = await current_user.received_connections.filter(
        is_accepted=False
    ).prefetch_related("from_user")

    out = []
    for connection in received:
        out.append(
            BaseUserOut(
                id=connection.from_user.id,
                username=connection.from_user.username,
                email=connection.from_user.email,
                created_at=connection.from_user.created_at,
                first_name=connection.from_user.first_name,
                last_name=connection.from_user.last_name,
            )
        )

    return out


@router.get(
    "/me/connections/sent",
    response_model=List[BaseUserOut],
    status_code=200,
    tags=["users"],
)
async def get_user_sent_connections(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's waiting sent connections
    """

    await current_user.fetch_related("sent_connections")
    sent = await current_user.sent_connections.filter(
        is_accepted=False
    ).prefetch_related("to_user")

    out = []
    for connection in sent:
        out.append(
            BaseUserOut(
                id=connection.to_user.id,
                username=connection.to_user.username,
                email=connection.to_user.email,
                created_at=connection.to_user.created_at,
                first_name=connection.to_user.first_name,
                last_name=connection.to_user.last_name,
            )
        )

    return out


@router.get(
    "/me/events",
    response_model=List[BaseEventOut],
    status_code=200,
    tags=["users", "events"],
)
async def get_user_events(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's events
    """

    await current_user.fetch_related("hosted_events")
    events = await current_user.hosted_events.order_by("-start_date")

    out = []
    for event in events:
        out.append(
            BaseEventOut(
                id=event.id,
                name=event.name,
                description=event.description,
                start_date=event.start_date,
                end_date=event.end_date,
                rate=event.rate,
            )
        )

    return out
