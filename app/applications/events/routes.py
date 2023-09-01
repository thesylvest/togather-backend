from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from tortoise.expressions import Q
from datetime import timezone

from app.core.base.utils import get_object_or_404, has_permission, extract_mentions_and_tags, extract_media_files
from app.core.auth.utils.contrib import get_current_active_user, get_current_active_user_optional
from .schemas import EventOut, EventCreate, EventUpdate, AttendeeOut, AttendeeCreate
from app.core.auth.utils.jwt import encode_jwt, decode_jwt
from app.applications.interactions.schemas import RateItem
from app.applications.interactions.models import Tag, Rate
from app.applications.organisations.models import Club
from .utils import EventFilter, AttendeeFilter
from app.applications.users.models import User
from app.core.base.paginator import Paginator
from .models import Event, Attendee

router = APIRouter()


@router.get("", tags=["events"], status_code=200)
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
    return await EventOut.serialize(event, current_user)


@router.post("", tags=["events"], status_code=201)
async def create_event(
    data: EventCreate,
    mentions_and_tags=Depends(extract_mentions_and_tags(EventCreate, ["name", "description"])),
    current_user: User = Depends(get_current_active_user),
):
    if data.host_club_id:
        club: Club = await get_object_or_404(Club, id=data.host_club_id)
        has_permission(club.is_admin, current_user)

    print(mentions_and_tags)
    urls, event_dict = extract_media_files(data=data)

    event = await Event.create(**event_dict, host_user=current_user)

    await Tag.bulk_create(
        Tag(name=name, item_id=event.id, item_type="Event") for name in data.tags
    )
    return {"created": await EventOut.serialize(event, current_user), "media_upload": urls}


@router.put("/{id}", tags=["events"], status_code=200)
async def update_event(
    id: int,
    data: EventUpdate,
    mentions_and_tags=Depends(extract_mentions_and_tags(EventUpdate, ["name", "description"])),
    current_user: User = Depends(get_current_active_user),
):
    print(mentions_and_tags)
    event: Event = await get_object_or_404(Event, id=id)
    await has_permission(event.is_host, current_user)

    urls, event_dict = extract_media_files(data=data, item=event)
    await event.update_from_dict(event_dict).save()

    if data.tags is not None:
        await Tag.filter(Q(item_id=id, item_type="Event") & ~Q(name__in=data.tags)).delete()
        for tag in data.tags:
            await Tag.get_or_create(name=tag, item_id=id, item_type="Event")
    return {"updated": event, "media_upload": urls}


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
    rate: RateItem,
    current_user: User = Depends(get_current_active_user),
):
    event: Event = await get_object_or_404(Event, id=id)
    try:
        rate_obj = await current_user.rates.get(item_id=event.id, item_type="Event")
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
        form_data=form_data.dict().get("form_data", None),
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
        "verification_link": encode_jwt({
            "id": event.name,
            "nbf": event.start_date.replace(tzinfo=timezone.utc).timestamp(),
            "exp": event.end_date.replace(tzinfo=timezone.utc).timestamp()
        })
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


@router.get("/forms", tags=["events"], status_code=200)
async def get_forms(
    event_id: int,
    paginator: Paginator = Depends(),
    current_user: User | None = Depends(get_current_active_user),
    forms=Depends(AttendeeFilter.dependency())
):
    return await paginator.paginate(forms, AttendeeOut, current_user)
