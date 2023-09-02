from fastapi import APIRouter, Depends
from tortoise.expressions import Q

from .schemas import ClubOut, PlaceOut, ClubCreate, ClubUpdate, PlaceCreate, PlaceUpdate, AdvertisementCreate, AdvertisementOut
from app.core.auth.utils.contrib import get_current_active_user, get_current_active_user_optional, get_current_active_superuser
from app.core.base.utils import get_object_or_404, has_permission
from .models import Club, Place, Membership, Advertisement
from app.applications.interactions.models import Tag
from app.applications.users.models import User
from app.core.base.paginator import Paginator
from app.core.base.extractor import Extractor
from .utils import ClubFilter, PlaceFilter


club_router = APIRouter()


@club_router.get("", tags=["clubs"], status_code=200)
async def get_clubs(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user_optional),
    clubs=Depends(ClubFilter.dependency())
):
    return await paginator.paginate(clubs, ClubOut, current_user)


@club_router.get("/{id}", tags=["clubs"])
async def get_club(
    id: int,
    current_user: User = Depends(get_current_active_user_optional),
):
    club = await get_object_or_404(Club, id=id)
    return await ClubOut.serialize(club, current_user)


@club_router.post("", tags=["clubs"])
async def create_club(
    data: ClubCreate,
    current_user: User = Depends(get_current_active_user),
):
    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    club_dict = data.dict(exclude_none=True, exclude=["media"])
    club_dict["media_dict"] = media_dict

    club = await Club.create(**club_dict)
    await Membership.create(club=club, user=current_user, is_admin=True)

    await Tag.bulk_create(
        Tag(name=name, item_id=club.id, item_type="Club") for name in data.tags
    )
    return {"created": await ClubOut.serialize(club, current_user), "media_upload": urls}


@club_router.put("/{id}", tags=["clubs"], status_code=200)
async def update_club(
    id: int,
    data: ClubUpdate,
    current_user: User = Depends(get_current_active_user),
):
    club: Club = await get_object_or_404(Club, id=id)
    await has_permission(club.is_admin, current_user)

    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    club_dict = data.dict(exclude_none=True, exclude=["media"])
    club_dict["media_dict"] = media_dict

    await club.update_from_dict(club_dict).save()

    if data.tags is not None:
        await Tag.filter(Q(item_id=id, item_type="Club") & ~Q(name__in=data.tags)).delete()
        for tag in data.tags:
            await Tag.get_or_create(name=tag, item_id=id, item_type="Club")
    return {"updated": await ClubOut.serialize(club, current_user), "media_upload": urls}


@club_router.post("/{id}/join", tags=["clubs"], status_code=200)
async def join(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    club: Club = await get_object_or_404(Club, id=id)
    if await club.members.filter(id=current_user.id).exists():
        await club.members.remove(current_user)
        await club.destroy_non_admin()
        return {"message": "successfully leaved"}
    await club.members.add(current_user)
    return {"message": "successfully joined"}


@club_router.post("/{id}/admins/{user_id}", tags=["clubs"], status_code=200)
async def add_admin(
    id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    club: Club = await get_object_or_404(Club, id=id)
    await has_permission(club.is_admin, current_user)

    membership: Membership = await get_object_or_404(Membership, user_id=user_id, club=club)

    membership.is_admin = not membership.is_admin
    await membership.save()

    if not membership.is_admin:
        await club.destroy_non_admin()

    return {
        "message": f"User {user_id}'s admin status changed: {membership.is_admin}",
        "membership_id": membership.id,
    }


place_router = APIRouter()


@place_router.get("", tags=["places"])
async def get_places(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user_optional),
    places=Depends(PlaceFilter.dependency())
):
    return await paginator.paginate(places, PlaceOut, current_user)


@place_router.get("/{id}", tags=["places"])
async def get_place(
    id: int,
    current_user: User = Depends(get_current_active_user_optional),
):
    place = await get_object_or_404(Place, id=id)
    return PlaceOut.serialize(place, current_user)


@place_router.post("", tags=["places"])
async def create_place(
    data: PlaceCreate,
    current_user: User = Depends(get_current_active_user),
):
    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    place_dict = data.dict(exclude_none=True, exclude=["media"])
    place_dict["media_dict"] = media_dict

    place = await Place.create(**place_dict)
    await place.owners.add(current_user)

    await Tag.bulk_create(
        Tag(name=name, item_id=place.id, item_type="Place") for name in data.tags
    )
    return {"created": await PlaceOut.serialize(place, current_user), "media_upload": urls}


@place_router.put("/{id}", tags=["places"], status_code=200)
async def update_place(
    id: int,
    data: PlaceUpdate,
    current_user: User = Depends(get_current_active_user),
):
    place: Place = await get_object_or_404(Place, id=id)
    await has_permission(place.is_owner, current_user)

    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    place_dict = data.dict(exclude_none=True, exclude=["media"])
    place_dict["media_dict"] = media_dict

    await place.update_from_dict(place_dict).save()

    if data.tags is not None:
        await Tag.filter(Q(item_id=id, item_type="Place") & ~Q(name__in=data.tags)).delete()
        for tag in data.tags:
            await Tag.get_or_create(name=tag, item_id=id, item_type="Place")
    return {"updated": await PlaceOut.serialize(place, current_user), "media_upload": urls}


@place_router.post("/{id}/owners/{user_id}", tags=["places"])
async def add_place_owner(
    id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    place: Place = await get_object_or_404(Place, id=id)
    has_permission(place.is_owner, current_user)
    user: User = await get_object_or_404(User, id=user_id)

    if await place.owners.filter(id=user.id).exists():
        await place.owners.remove(user)
        await place.destroy_non_owner()
        return {"message": "successfully removed"}
    await place.owners.add(user)
    return {"message": "successfully added"}


@place_router.post("/{id}/owners", tags=["places"])
async def leave_place(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    place: Place = await get_object_or_404(Place, id=id)
    await place.owners.remove(current_user)
    await place.destroy_non_owner()
    return {"message": "successfully removed"}


@place_router.get("/{id}/advertisements", tags=["places"])
async def get_place_ads(
    id: int,
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user_optional),
):
    place: Place = await get_object_or_404(Place, id=id)
    return await paginator.paginate(place.advertisements.all(), AdvertisementOut, current_user)


@place_router.post("/{id}/advertisements", tags=["places"])
async def add_place_ad(
    id: int,
    data: AdvertisementCreate,
    current_user: User = Depends(get_current_active_user),
):
    place: Place = await get_object_or_404(Place, id=id)
    has_permission(place.is_owner, current_user)

    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    add_dict = data.dict(exclude_none=True, exclude=["media"])
    add_dict["media_dict"] = media_dict

    ad = await Advertisement.create(**add_dict, place=place)

    return {
        "message": "Advertisement added successfully.",
        "ad": AdvertisementOut.serialize(ad, current_user),
    }


@place_router.post("/{id}", tags=["places"])
async def verify_place(
    id: int,
    current_user: User = Depends(get_current_active_superuser),
):
    place: Place = await get_object_or_404(Place, id=id)
    place.is_valid = not place.is_valid
    await place.save()

    return {"message": f"New status of place {id} is {place.is_valid}"}
