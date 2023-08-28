from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from datetime import timezone

from app.core.auth.utils.contrib import get_current_active_user, get_current_active_user_optional
from .schemas import EventOut, EventCreate, EventUpdate, AttendeeOut, AttendeeCreate, EventRate
from app.core.base.utils import get_object_or_404, has_permission
from app.core.auth.utils.jwt import encode_jwt, decode_jwt
from app.applications.interactions.models import Tag, Rate
from .utils import EventFilter, AttendeeFilter
from app.applications.users.models import User
from app.core.base.paginator import Paginator
from app.core.base.media_manager import S3
from .models import Event, Attendee

router = APIRouter()


@router.get("/", tags=["events"], status_code=200)
async def get_events(
    paginator: Paginator = Depends(),
    current_user: User | None = Depends(get_current_active_user_optional),
    events=Depends(EventFilter.dependency())
):
    return await paginator.paginate(events, EventOut, current_user)


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
    urls, media = zip(*[await S3.upload_file(file_dict["file_type"]) for file_dict in event_in.media])

    jwt = encode_jwt({
        "id": event_in.name,
        "nbf": event_in.start_date.replace(tzinfo=timezone.utc).timestamp(),
        "exp": event_in.end_date.replace(tzinfo=timezone.utc).timestamp()
    })

    event = await Event.create(
        **event_in.dict(exclude_unset=True, exclude=["media"]),
        host_user=current_user,
        media=media,
        verification_link=jwt,
    )

    for tag in event_in.tags:
        await Tag.create(name=tag, item_id=event.id, item_type="Event")
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
    media = []
    for media_dict in event_in.media:
        if media_dict.get("name", None) not in event.media:
            url, name = await S3.upload_file(media_dict["file_type"])
            urls.append(url)
        else:
            name = media_dict["name"]
        media.append(name)

    await event.update_from_dict(**event_in.dict(exclude_none=True), media=media)

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
    if await event.attendees.filter(id=current_user.id).exists():
        await event.attendees.remove(current_user)
        return {"message": "successfully unattending"}
    if event.form:
        if form_data is None or form_data == dict():
            raise HTTPException(
                status_code=400,
                detail="Form is needed"
            )
    await Attendee.create(
        form_data=form_data.dict()["form_data"],
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


@router.get("/{id}/verify", tags=["events"], status_code=200)
async def get_verification(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await get_object_or_404(Event, id=id)
    await has_permission(event.is_host, current_user)

    return {
        "verification_link": event.verification_link
    }


@router.get("/verify/{token}", tags=["events"], status_code=200)
async def verify(
    token: str,
    current_user: User = Depends(get_current_active_user_optional),
):
    if not current_user:
        return RedirectResponse(url=f"/api/auth/login/?redirect_url=/api/events/verify/{token}")  # TODO: implement this login url with redirect capabilities
    try:
        payload = decode_jwt(token)
    except ExpiredSignatureError:
        return HTTPException(status_code=401, detail="link has been expired")
    except JWTClaimsError:
        return HTTPException(status_code=401, detail="link has not been activated")
    except JWTError:
        return HTTPException(status_code=401, detail="link is wrong")
    event: Event = get_object_or_404(Event, name=payload["name"])
    attend: Attendee = Attendee.get_or_none(event=event, user=current_user)
    if attend:
        attend.is_verified = True
        attend.save()
    else:
        attend: Attendee = await Attendee.create(event=event, user=current_user, is_verified=True)
    return attend


@router.get("/{event_id}/forms", tags=["events"], status_code=200)
async def get_forms(
    event_id: int,
    paginator: Paginator = Depends(),
    current_user: User | None = Depends(get_current_active_user),
    forms=Depends(AttendeeFilter.dependency())
):
    return await paginator.paginate(forms, AttendeeOut, current_user)


#  filter by hide and block, tag system embedded to text
