from fastapi import APIRouter, Request, Depends, Query, HTTPException

from app.core.auth.utils.contrib import get_current_active_user, get_current_active_user_optional
from .schemas import EventOut, EventCreate, EventUpdate, AttendeeOut, AttendeeCreate, EventRate
from app.core.base.utils import get_object_or_404, has_permission
from app.applications.interactions.models import Tag, Rate
from .utils import EventFilter, AttendeeFilter
from app.applications.users.models import User
from app.core.base.paginator import paginate
from app.core.base.media_manager import S3
from .models import Event, Attendee

router = APIRouter()


@router.get("/", tags=["events"], status_code=200)
async def get_events(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, title="Page size"),
    current_user: User | None = Depends(get_current_active_user_optional),
    events=Depends(EventFilter.dependency())
):
    return await paginate(events, page, page_size, request, EventOut, current_user)


@router.get("/{id}", tags=["events"], status_code=200)
async def get_event(
    id: int,
    current_user: User = Depends(get_current_active_user_optional),
):
    event = await get_object_or_404(Event, id=id)
    return EventOut.serialize(event, current_user)


@router.post("/", tags=["events"], status_code=201)
async def create_event(
    event_in: EventCreate,
    current_user: User = Depends(get_current_active_user),
):
    urls, media = zip(*[await S3.upload_file(file_type) for file_type in event_in.media])
    event = await Event.create(
        **event_in.dict(exclude_unset=True, exclude=["media"]),
        host_user=current_user,
        media=media
    )

    for tag in event_in.tags:
        await Tag.create(name=tag, item_id=event.id, item_type=Tag.ModelType.event)
    return {
        "created": event,
        "media_upload": urls
    }


@router.put("/{id}", tags=["events"], status_code=200)
async def update_event(
    id: int,
    event_in: EventUpdate,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await get_object_or_404(Event, id=id)
    await has_permission(event.is_host, current_user)

    urls = []
    if event_in.media:
        for media_dict in event_in.media:
            url, event.media[media_dict["no"]] = await S3.upload_file(media_dict["file_type"])
            urls.append(url)

    await event.update_from_dict(**event_in.dict(exclude_none=True))

    if event_in.tags:
        for tag in await Tag.filter(item_id=id, item_type=Tag.ModelType.event):
            if tag.name not in event_in.tags:
                tag.delete()
        for tag in event_in.tags:
            await Tag.get_or_create(name=tag, item_id=event.id, item_type=Tag.ModelType.event)
    return {
        "updated": event,
        "media_upload": urls
    }


@router.delete("/{id}", tags=["events"], status_code=200)
async def delete_event(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await get_object_or_404(Event, id=id)
    await has_permission(event.is_host, current_user)

    await event.delete()
    return event


@router.post("/{id}/rate", tags=["events"], status_code=200)
async def rate_event(
    id: int,
    rate: EventRate,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await get_object_or_404(Event, id=id)
    try:
        rate_obj = await (await Rate.get_by_item(item=event)).get(rater=current_user)
        rate_obj.rate = rate.rate
        await rate_obj.save()
    except Exception:
        rate_obj = await Rate.create(item_id=event.id, item_type="Event", rate=rate.rate, rater=current_user)
    return rate_obj


@router.post("/{id}/attend", tags=["events"], status_code=200)
async def attend(
    id: int,
    form_data: AttendeeCreate,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await get_object_or_404(Event, id=id)
    if await event.attendees.exists(id=current_user.id):
        await event.attendees.remove(current_user)
        return {"message": "successfully unattending"}
    if event.form:
        if form_data is None or form_data == dict():
            raise HTTPException(
                status_code=400,
                detail="Form is needed"
            )
    await Attendee.create(
        form_data=form_data,
        user=current_user,
        event=event
    )
    return {"message": "successfully attended"}


@router.post("/{id}/verify_user/{user_id}", tags=["events"], status_code=200)
async def verify_user(
    id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await get_object_or_404(Event, id=id)
    await has_permission(event.is_host, current_user)

    attendee: Attendee = await get_object_or_404(Attendee, user_id=user_id, event_id=id)
    attendee.is_verified = not attendee.is_verified
    await attendee.save()
    return {"verification status": attendee.is_verified}


@router.get("/{id}/verification", tags=["events"], status_code=200)
async def verification(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await get_object_or_404(Event, id=id)
    await has_permission(event.is_host, current_user)

    return {
        "qr_code": event.qr_code,
        "verification_link": event.verification_link
    }


@router.get("/{event_id}/forms", tags=["events"], status_code=200)
async def get_forms(
    request: Request,
    event_id: int,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, title="Page size"),
    current_user: User | None = Depends(get_current_active_user),
    forms=Depends(AttendeeFilter.dependency())
):
    return await paginate(forms, page, page_size, request, AttendeeOut, current_user)


# join, verify, qr code, hide, report, filter by hide and block, tag system embedded to text(
