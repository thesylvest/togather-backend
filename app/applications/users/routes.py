from fastapi import BackgroundTasks, APIRouter, Depends, HTTPException, Request, Query
from tortoise.expressions import Q, Subquery

from app.core.auth.utils.contrib import (
    get_current_active_superuser,
    get_current_active_user,
)
from app.core.auth.utils.password import get_password_hash
from .schemas import UserOut, UserCreate, UserUpdate
from app.applications.events.schemas import EventOut
from app.core.base.paginator import paginate
from .models import User, Connection
from app.settings import config

router = APIRouter()


@router.get("/", status_code=200, tags=["users"])
async def read_users(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve users.
    """
    users = User.all()
    return await paginate(users, page, page_size, request, UserOut, current_user)


@router.post("/", status_code=201, tags=["users"])
async def create_user(
    *,
    user_in: UserCreate,
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
    db_user = UserCreate(
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
    return await UserOut.serialize(created_user, current_user)


@router.put("/me", status_code=200, tags=["users"])
async def update_user_me(
    user_in: UserUpdate, current_user: User = Depends(get_current_active_user)
):
    """
    Update own user.
    """
    user = current_user

    for field, value in user_in.create_update_dict().items():
        if value is not None:
            setattr(user, field, value)

    await user.save()
    return await UserOut.serialize(current_user, current_user)


@router.get("/me", status_code=200, tags=["users"])
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's info.
    """
    return await UserOut.serialize(current_user, current_user)


@router.get("/{user_id}", status_code=200, tags=["users"])
async def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific user's info by username.
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    return await UserOut.serialize(user, current_user)


@router.put("/{user_id}", status_code=200, tags=["users"])
async def update_user(
    user_id: int,
    user_in: UserUpdate,
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
    return await UserOut.serialize(user, current_user)


@router.get(
    "/{user_id}/connections",
    status_code=200,
    tags=["users"],
)
async def get_user_connections(
    user_id: int,
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific user's connections by user ID.
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )

    connections = User.filter(
        Q(id__in=Subquery(Connection.filter(is_accepted=True, from_user=user).values('to_user_id'))) |
        Q(id__in=Subquery(Connection.filter(is_accepted=True, to_user=user).values('from_user_id')))
    )

    return await paginate(connections, page, page_size, request, UserOut, current_user)


@router.post(
    "/{user_id}/connections",
    status_code=200,
    tags=["users"],
)
async def user_connect(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    if user == current_user:
        raise HTTPException(
            status_code=403,
            detail="Can't connect with self",
        )
    await Connection.create(from_user=current_user, to_user=user, is_accepted=False)
    return "Connection request sent"


@router.get(
    "/me/connections/received",
    status_code=200,
    tags=["users"],
)
async def get_user_received_connections(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's waiting received connections
    """
    received = current_user.received_connections.filter(
        is_accepted=False
    ).prefetch_related("from_user")
    return await paginate(received, page, page_size, request, UserOut, current_user)


@router.get(
    "/me/connections/sent",
    status_code=200,
    tags=["users"],
)
async def get_user_sent_connections(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's waiting sent connections
    """
    sent = current_user.sent_connections.filter(
        is_accepted=False
    ).prefetch_related("to_user")
    return await sent
    # return await paginate(sent, page, page_size, request, UserOut, current_user)
