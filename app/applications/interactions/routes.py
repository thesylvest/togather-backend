from fastapi import APIRouter, Depends

from app.core.auth.utils.contrib import get_current_active_user
from app.applications.users.models import User
from .schemas import HideCreate, ReportCreate
from .models import Category, Hide, Report

router = APIRouter()


@router.post("/hides", tags=["interactions"], status_code=200)
async def hide(
    hide: HideCreate,
    current_user: User = Depends(get_current_active_user)
):
    return await Hide.get_or_create(**hide.dict(), hider=current_user)


@router.post("/report", tags=["interactions"], status_code=200)
async def report(
    report: ReportCreate,
    current_user: User = Depends(get_current_active_user)
):
    report: Report = await Report.get_or_none(item_type=report.item_type, item_id=report.item_id, reporter=current_user)
    if report:
        await report.update_from_dict({"reason": report.reason})
    return await Report.create(**report.dict(), reporter=current_user)


@router.get("/categories", tags=["categories"], status_code=200)
async def get_categories():
    return await Category.all()
