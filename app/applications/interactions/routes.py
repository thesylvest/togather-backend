from fastapi import APIRouter, Request, Depends, Query

from app.core.auth.utils.contrib import get_current_active_user
from app.applications.users.models import User
from app.core.base.paginator import paginate
from .schemas import NotificationOut
from .models import Category

notification_router = APIRouter()
category_router = APIRouter()


@notification_router.get("/", tags=["notifications"], status_code=200)
async def get_notifications(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve notifications of me.
    """
    return await paginate(current_user.notifications.all(), page, page_size, request, NotificationOut, current_user)


@category_router.get("/", tags=["categories"], status_code=200)
async def get_categories():
    return await Category.all()


@category_router.post("/", tags=["categories"], status_code=201)
async def create_categories():
    for i in range(10):
        await Category.get_or_create(name=f"cat{i}", picture=None)
    return await Category.all()
