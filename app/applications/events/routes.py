from fastapi import APIRouter, Request, Depends, Query, HTTPException

from app.core.auth.utils.contrib import get_current_active_user
from app.applications.users.models import User
from app.core.base.paginator import paginate
from .schemas import EventOut, EventCreate
from .models import Event, Category

category_router = APIRouter()
router = APIRouter()


@router.get("/", tags=["events"], status_code=200)
async def get_events(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve events.
    """
    events = Event.all()
    return await paginate(events, page, page_size, request, EventOut, current_user)


@router.get("/{event_id}", tags=["events"], status_code=200)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve event.
    """
    event = await Event.get(id=event_id)
    return EventOut.serialize(event, current_user)


@router.post("/", tags=["events"], status_code=201)
async def create_event(
    event_in: EventCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create new event.
    """
    category = await Category.get(name=event_in.category)
    if not category:
        raise HTTPException(
            status_code=400, detail="The category doesn't exist"
        )
    event_in.category = category

    event = Event(**event_in.create_update_dict(), host_user_id=current_user.id)
    await event.save()
    return event


@category_router.get("/", tags=["categories"], status_code=200)
async def get_categories():
    """
    Retrieve categories.
    """
    categories = await Category.all()
    return categories


@category_router.post("/", tags=["categories"], status_code=201)
async def create_categories():
    """
    Create categories.
    """
    for i in range(10):
        await Category.get_or_create(name=f"cat{i}", picture=None)
    return await Category.all()
