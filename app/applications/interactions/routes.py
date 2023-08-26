from fastapi import APIRouter, Request, Depends, Query

from .schemas import NotificationOut, HideCreate, ReportCreate, HideOut, ReportOut
from app.core.auth.utils.contrib import get_current_active_user
from app.applications.users.models import User
from app.core.base.paginator import paginate
from .models import Category, Hide, Report

router = APIRouter()


@router.get("/notifications", tags=["notifications"], status_code=200)
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


@router.get("/hides", tags=["inform"], status_code=200)
async def get_hidden(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve hidden items of me.
    """
    return await paginate(Hide.filter(hider=current_user), page, page_size, request, HideOut, current_user)


@router.post("/hides", tags=["inform"], status_code=200)
async def hide(
    hide: HideCreate,
    current_user: User = Depends(get_current_active_user)
):
    return await Hide.create(**hide.dict(), hider=current_user)


@router.get("/reports", tags=["inform"], status_code=200)
async def get_reports(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve hidden items of me.
    """
    return await paginate(Report.filter(reporter=current_user), page, page_size, request, ReportOut, current_user)


@router.post("/report", tags=["inform"], status_code=200)
async def report(
    report: ReportCreate,
    current_user: User = Depends(get_current_active_user)
):
    return await Report.create(**report.dict(), reporter=current_user)


@router.get("/categories", tags=["categories"], status_code=200)
async def get_categories():
    return await Category.all()


@router.post("/categories", tags=["categories"], status_code=201)
async def create_categories():
    for i in range(10):
        await Category.get_or_create(name=f"cat{i}", picture=None)
    return await Category.all()
