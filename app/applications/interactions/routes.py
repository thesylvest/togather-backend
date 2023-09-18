from fastapi import APIRouter, Depends

from app.core.auth.utils.contrib import get_current_active_user, get_current_active_user_optional
from .schemas import HideCreate, ReportCreate, CategoryOut
from app.applications.users.models import User
from app.core.base.paginator import Paginator
from .models import Category, Hide, Report
from .utils import TagFilter

interaction_router = APIRouter()


@interaction_router.post("/hides/", tags=["interactions"], status_code=200)
async def hide(
    hide: HideCreate,
    current_user: User = Depends(get_current_active_user)
):
    return await Hide.get_or_create(**hide.dict(), hider=current_user)


@interaction_router.post("/report/", tags=["interactions"], status_code=200)
async def report(
    report: ReportCreate,
    current_user: User = Depends(get_current_active_user)
):
    item: Report = await Report.get_or_none(item_type=report.item_type, item_id=report.item_id, reporter=current_user)
    if item:
        return await item.update_from_dict({"reason": report.reason}).save()
    return await Report.create(**report.dict(), reporter=current_user)


@interaction_router.get("/categories/", tags=["interactions"], status_code=200)
async def get_categories():
    categories = await CategoryOut.from_queryset(Category.all())
    return {
        "has_next": False,
        "count": len(categories),
        "results": categories
    }


@interaction_router.get("/tags/", tags=["interactions"], status_code=200)
async def get_tags(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user_optional),
    tags=Depends(TagFilter.dependency())
):
    tags = tags[0].all().distinct().limit(
        paginator.page_size
    ).offset(
        (paginator.page - 1) * paginator.page_size
    ).values("name")
    return {
        "has_next": True,
        "count": 9999999,
        "results": await tags
    }
