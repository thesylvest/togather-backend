from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import Q

from app.core.auth.utils.contrib import get_current_active_user_optional, get_current_active_user
from app.core.base.utils import get_object_or_404, extract_mentions_and_tags, extract_media_files
from app.applications.interactions.schemas import NotificationOut, ReportOut, HideOut
from app.applications.interactions.utils import HideFilter, ReportFilter
from app.core.auth.utils.password import get_password_hash
from app.applications.interactions.models import Category
from .schemas import UserOut, UserUpdate, LocationUpdate
from app.core.base.paginator import Paginator
from .models import User, Connection
from .utils import UserFilter

router = APIRouter()


@router.get("", status_code=200, tags=["users"])
async def read_users(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user_optional),
    users=Depends(UserFilter.dependency())
):
    return await paginator.paginate(users, UserOut, current_user)


@router.put("/me", status_code=200, tags=["users"])
async def update_me(
    data: UserUpdate,
    mentions_and_tags=Depends(extract_mentions_and_tags(UserUpdate, ["bio"])),
    current_user: User = Depends(get_current_active_user)
):
    print(mentions_and_tags)
    urls, user_dict = extract_media_files(data=data, item=current_user)

    if data.password is not None:
        user_dict["password_hash"] = get_password_hash(data.password)

    try:
        await current_user.categories.add(
            *(await Category.filter(id__in=data.categories))
        )
        await current_user.categories.remove(
            *(await Category.filter(
                ~Q(id__in=data.categories) & Q(follower=current_user)
            ))
        )
        user_dict.pop("categories")
    except Exception:
        pass

    await current_user.update_from_dict(user_dict).save()

    return await UserOut.serialize(current_user, current_user)


@router.put("/me/location", status_code=200, tags=["users"])
async def update_my_location(
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_active_user)
):
    await current_user.update_from_dict(**location_data.dict())
    return location_data


@router.delete("/me", status_code=200, tags=["users"])
async def delete_me(
    current_user: User = Depends(get_current_active_user)
):
    await current_user.delete()
    return current_user


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


@router.post("/{id}/block", status_code=200, tags=["users"])
async def user_block(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    user = await get_object_or_404(User, id=id)
    if user == current_user:
        raise HTTPException(
            status_code=403,
            detail="Can't block self",
        )
    if await current_user.blocked_users.filter(id=id).exists():
        await current_user.blocked_users.remove(user)
        return "User unblocked"
    else:
        await Connection.filter(Q(from_user=user, to_user=current_user) | Q(from_user=current_user, to_user=user)).delete()
        await current_user.blocked_users.add(user)
        return "User blocked"


@router.get("/me/notifications", status_code=200, tags=["users"])
async def get_my_notifications(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    return await paginator.paginate(current_user.notifications.all(), NotificationOut, current_user)


@router.get("/me/notifications/count", status_code=200, tags=["users"])
async def get_my_unread_notifications_count(
    current_user: User = Depends(get_current_active_user),
):
    return current_user.unread_notifications


@router.get("/me/reports", status_code=200, tags=["users"])
async def get_my_reports(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
    reports=Depends(ReportFilter.dependency())
):
    return await paginator.paginate(reports.filter(reporter=current_user), ReportOut, current_user)


@router.get("/me/blocked", status_code=200, tags=["users"])
async def get_blocked_users(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    return await paginator.paginate(current_user.blocked_users, UserOut, current_user)


@router.get("/me/hides", status_code=200, tags=["users"])
async def get_my_hides(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
    hidden=Depends(HideFilter.dependency())
):
    return await paginator.paginate(hidden.filter(hider=current_user), HideOut, current_user)


@router.get("/me/connections/received", status_code=200, tags=["users"])
async def get_connection_requests_to_me(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    received = User.filter(sent_connections__to_user=current_user, sent_connections__is_accepted=False)
    return await paginator.paginate(received, UserOut, current_user)


@router.get("/me/connections/sent", status_code=200, tags=["users"])
async def get_connection_requests_from_me(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    sent = User.filter(received_connections__from_user=current_user, received_connections__is_accepted=False)
    return await paginator.paginate(sent, UserOut, current_user)
