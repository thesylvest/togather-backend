from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import Q

from app.core.auth.utils.contrib import get_current_active_user_optional, get_current_active_user
from app.applications.interactions.schemas import NotificationOut, ReportOut
from app.applications.interactions.utils import ReportFilter
from app.core.auth.utils.password import get_password_hash
from app.applications.interactions.models import Category
from .schemas import UserOut, UserUpdate, LocationUpdate
from app.core.base.utils import get_object_or_404
from app.core.base.extractor import Extractor
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


@router.get("/{id}", status_code=200, tags=["users"])
async def read_user(
    id: int,
    current_user: User = Depends(get_current_active_user_optional),
):
    user = await get_object_or_404(User, id=id)
    return await UserOut.serialize(user, current_user)


@router.put("/me", status_code=200, tags=["users"])
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    extractor = Extractor(data)
    urls, media_dict = extractor.media_files(current_user)
    user_dict = data.dict(exclude_none=True, exclude=["media", "interests"])
    user_dict["media_dict"] = media_dict

    if data.password is not None:
        user_dict["password_hash"] = get_password_hash(data.password)

    if data.interests:
        await current_user.interests.add(
            *(await Category.filter(id__in=data.interests))
        )
        try:
            await current_user.interests.remove(
                *(await Category.filter(
                    ~Q(id__in=data.interests) & Q(follower=current_user)
                ))
            )
        except Exception:
            pass

    await current_user.update_from_dict(user_dict).save()

    return await UserOut.serialize(current_user, current_user)


@router.put("/me/location", status_code=200, tags=["users"])
async def update_my_location(
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_active_user)
):
    await current_user.update_from_dict(location_data.dict()).save()
    return location_data


@router.delete("/me", status_code=200, tags=["users"])
async def delete_me(
    current_user: User = Depends(get_current_active_user)
):
    await current_user.delete()
    return current_user


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
        return False
    recv: Connection = await Connection.get_or_none(from_user=user, to_user=current_user)
    if recv:
        if recv.is_accepted:
            return False
        recv.is_accepted = True
        await recv.save()
        return True
    await Connection.create(from_user=current_user, to_user=user, is_accepted=False)
    return True


@router.post("/{id}/disconnect", status_code=200, tags=["users"])
async def user_disconnect(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    user = await get_object_or_404(User, id=id)
    if user == current_user:
        raise HTTPException(
            status_code=403,
            detail="Can't disconnect with self",
        )
    sent: Connection = await Connection.get_or_none(from_user=current_user, to_user=user)
    if sent:
        await sent.delete()
        return True
    recv: Connection = await Connection.get_or_none(from_user=user, to_user=current_user)
    if recv:
        await recv.delete()
        return True
    return False


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
    return await paginator.paginate((current_user.notifications.all(), []), NotificationOut, current_user)


@router.get("/me/notifications/count", status_code=200, tags=["users"])
async def get_my_unread_notifications_count(
    zero: bool = False,
    current_user: User = Depends(get_current_active_user),
):
    if zero:
        cnt = current_user.unread_notifications
        current_user.unread_notifications = 0
        await current_user.save()
        return cnt
    return current_user.unread_notifications


@router.get("/me/reports", status_code=200, tags=["users"])
async def get_my_reports(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
    reports=Depends(ReportFilter.dependency())
):
    return await paginator.paginate((reports[0].filter(reporter=current_user), reports[1]), ReportOut, current_user)


@router.get("/me/blocked", status_code=200, tags=["users"])
async def get_blocked_users(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    return await paginator.paginate((current_user.blocked_users.all(), []), UserOut, current_user)


@router.get("/me/connections/received", status_code=200, tags=["users"])
async def get_connection_requests_to_me(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    received = User.filter(sent_connections__to_user=current_user, sent_connections__is_accepted=False), []
    return await paginator.paginate(received, UserOut, current_user)


@router.get("/me/connections/sent", status_code=200, tags=["users"])
async def get_connection_requests_from_me(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    sent = User.filter(received_connections__from_user=current_user, received_connections__is_accepted=False), []
    return await paginator.paginate(sent, UserOut, current_user)
