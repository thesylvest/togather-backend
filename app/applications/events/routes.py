from fastapi import APIRouter, Request, Depends, Query, HTTPException
from app.applications.users.models import User
from app.core.auth.utils.contrib import get_current_active_user
from app.core.base.paginator import paginate
from app.applications.events.models import Event, Category
from app.applications.events.schemas import BaseEventOut, BaseEventCreate

router = APIRouter()


@router.get("/", tags=["events"], status_code=200)
async def get_events(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
):
    """
    Retrieve events.
    """
    events = Event.all()
    return await paginate(events, page, page_size, request, BaseEventOut, None)

@router.get("/categories", tags=["events"], status_code=200)
async def get_categories():
    """
    Retrieve categories.
    """
    categories = await Category.all()
    return categories


@router.get("/{event_id}", tags=["events"], status_code=200)
async def get_event(
    event_id: int,
):
    """
    Retrieve event.
    """
    event = await Event.get(id=event_id)
    return event


@router.post("/", tags=["events"], status_code=201)
async def create_event(
    event_in: BaseEventCreate,
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
