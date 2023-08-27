from fastapi import APIRouter, Depends, HTTPException, Request, Query

from app.core.auth.utils.contrib import (
    get_current_active_user_optional,
    get_current_active_user,
)
from app.core.base.utils import get_object_or_404
from app.core.base.paginator import paginate
from .schemas import UserOut, UserUpdate
from .models import User, Connection
from .utils import UserFilter

router = APIRouter()


@router.get("/", status_code=200, tags=["users"])
async def read_users(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user_optional),
    users=Depends(UserFilter.dependency())
):
    return await paginate(users, page, page_size, request, UserOut, current_user)


@router.put("/me", status_code=200, tags=["users"])
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    user = current_user

    for field, value in user_in.create_update_dict().items():
        if value is not None:
            setattr(user, field, value)

    await user.save()
    return await UserOut.serialize(current_user, current_user)


@router.get("/{id}", status_code=200, tags=["users"])
async def read_user(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    user = await get_object_or_404(User, id=id)
    return await UserOut.serialize(user, current_user)


@router.post("/{id}/connect", status_code=200, tags=["users"])
async def user_connect(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    user = await get_object_or_404(User, id=id)
    if user == current_user:
        raise HTTPException(
            status_code=403,
            detail="Can't connect with self",
        )
    sent: Connection = await Connection.get_or_none(from_user=current_user, to_user=user)
    if sent:
        return await sent.delete()
    recv: Connection = await Connection.get_or_none(from_user=user, to_user=current_user)
    if recv:
        if recv.is_accepted:
            return await recv.delete()
        recv.is_accepted = True
        return await recv.save()
    return await Connection.create(from_user=current_user, to_user=user, is_accepted=False)


@router.get("/me/connections/received", status_code=200, tags=["users"])
async def get_user_received_connections(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    received = current_user.received_connections.filter(
        is_accepted=False
    ).prefetch_related("from_user")
    return await paginate(received, page, page_size, request, UserOut, current_user)


@router.get("/me/connections/sent", status_code=200, tags=["users"])
async def get_user_sent_connections(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    sent = current_user.sent_connections.filter(
        is_accepted=False
    ).prefetch_related("to_user")
    return await paginate(sent, page, page_size, request, UserOut, current_user)
