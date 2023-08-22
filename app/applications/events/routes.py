from fastapi import APIRouter, Request, Depends, Query, HTTPException

from app.core.auth.utils.contrib import get_current_active_user, get_current_active_user_optional
from .schemas import EventOut, EventCreate, EventUpdate
from app.applications.interactions.models import Tag
from app.applications.users.models import User
from app.core.base.paginator import paginate
from .models import Event, Category
from .utils import EventFilter

category_router = APIRouter()
router = APIRouter()


@router.get("/", tags=["events"], status_code=200)
async def get_events(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User | None = Depends(get_current_active_user_optional),
    events=Depends(EventFilter.dependency())
):
    return await paginate(events, page, page_size, request, EventOut, current_user)


@router.get("/{event_id}", tags=["events"], status_code=200)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
):
    event = await Event.get(id=event_id)
    return EventOut.serialize(event, current_user)


@router.post("/", tags=["events"], status_code=201)
async def create_event(
    event_in: EventCreate,
    current_user: User = Depends(get_current_active_user),
):
    category = await Category.get(name=event_in.category)
    if not category:
        raise HTTPException(
            status_code=400, detail="The category doesn't exist"
        )
    event_in.category = category

    event = Event(**event_in.create_update_dict(), host_user_id=current_user.id)
    await event.save()

    for tag in event_in.tags:
        await Tag.create(name=tag, item_id=event.id, item_type=Tag.ModelType.event)
    return event


@router.put("/{event_id}", tags=["events"], status_code=200)
async def update_event(
    event_id: int,
    event_in: EventUpdate,
    current_user: User = Depends(get_current_active_user),
):
    event = await Event.filter(id=event_id).update(**event_in.dict(exclude_none=True))

    if event_in.tags:
        for tag in await Tag.filter(item_id=event_id, item_type=Tag.ModelType.event):
            if tag.name not in event_in.tags:
                tag.delete()
        for tag in event_in.tags:
            await Tag.get_or_create(name=tag, item_id=event.id, item_type=Tag.ModelType.event)
    return event


@router.delete("/{event_id}", tags=["events"], status_code=200)
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await Event.get_or_none(id=event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    if not event.is_host(current_user):
        raise HTTPException(
            status_code=403,
            detail="Insufficient privilege"
        )
    await event.delete()
    return event


@category_router.get("/", tags=["categories"], status_code=200)
async def get_categories():
    return await Category.all()


@category_router.post("/", tags=["categories"], status_code=201)
async def create_categories():
    for i in range(10):
        await Category.get_or_create(name=f"cat{i}", picture=None)
    return await Category.all()
