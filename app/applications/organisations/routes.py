from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.applications.organisations.models import (
    Club,
    Place,
    Membership,
    Advertisement,
    Ownership,
)
from app.applications.organisations.schemas import (
    ClubOut,
    PlaceOut,
    ClubIn,
    PlaceIn,
    AdvertisementIn,
    ClubMembersOut,
)
from app.core.auth.utils.contrib import get_current_active_user
from app.applications.users.schemas import UserOut
from app.applications.users.models import User
from app.core.base.paginator import paginate


club_router, place_router = APIRouter(), APIRouter()


@club_router.get("", tags=["clubs"])
async def get_clubs(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all clubs."""
    clubs = Club.all()
    return await paginate(clubs, page, page_size, request, ClubOut, current_user)


@place_router.get("", tags=["places"])
async def get_places(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all clubs."""
    places = Place.all()
    return await paginate(places, page, page_size, request, PlaceOut, current_user)


@club_router.get("/{club_id}", tags=["clubs"])
async def get_club(
    club_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Get a club."""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return ClubOut.serialize(club, current_user)


@place_router.get("/{place_id}", tags=["places"])
async def get_place(
    place_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Get a place."""
    place = await Place.get_or_none(id=place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return PlaceOut.serialize(place, current_user)


@club_router.get("/{club_id}/members", tags=["clubs"])
async def get_club_members(
    club_id: int,
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all members of a club."""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    members = Membership.filter(club=club)
    return await paginate(members, page, page_size, request, ClubMembersOut, current_user)


@club_router.get("/{club_id}/admins", tags=["clubs"])
async def get_club_admins(
    club_id: int,
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all admins of a club."""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    members = Membership.filter(club=club, is_admin=True)
    return await paginate(members, page, page_size, request, ClubMembersOut, current_user)


@club_router.post("/{club_id}/admins/{user_id}", tags=["clubs"])
async def add_club_admin(
    club_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Add an admin to a club."""
    user = await User.get_or_none(id=user_id)
    # Check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    club = await Club.get_or_none(id=club_id)
    # Check if the club exists
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    if not await Membership.exists(user=user, club=club):
        raise HTTPException(status_code=400, detail="User is not a member of the club")

    # Check if the user is already an admin of the club
    if await Membership.exists(user=user, club=club, is_admin=True):
        raise HTTPException(
            status_code=400, detail="User is already an admin of the club"
        )

    # Create a new membership record
    membership = await Membership.get(user=user, club=club)
    membership.is_admin = True
    await membership.save()

    return {
        "message": f"User {user_id} added as an admin to club {club_id}",
        "membership_id": membership.id,
    }


@place_router.get("/{place_id}/ads", tags=["places"])
async def get_place_ads(
    place_id: int,
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all ads of a place."""
    place = await Place.get_or_none(id=place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return await place.advertisements.all()  # TODO: make this paginated


@place_router.post("/{place_id}/ads", tags=["places"])
async def add_place_ad(
    place_id: int,
    ad_in: AdvertisementIn,
    current_user: User = Depends(get_current_active_user),
):
    """Add an ad to a place."""
    place = await Place.get_or_none(id=place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    ad = await Advertisement.create(**ad_in.to_dict(), place=place)

    return {
        "message": "Ad added successfully.",
        "ad": ad,
    }


@place_router.get("/{place_id}/owners", tags=["places"])
async def get_place_owners(
    place_id: int,
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all owners of a place."""
    place = await Place.get_or_none(id=place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    owners = place.owners.all()
    return await paginate(owners, page, page_size, request, UserOut, current_user)


@place_router.post("/{place_id}/owners/{user_id}", tags=["places"])
async def add_place_owner(
    place_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Add an owner to a place."""
    user = await User.get_or_none(id=user_id)
    # Check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    place = await Place.get_or_none(id=place_id)
    # Check if the place exists
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    # Check if the user is already an owner of the place
    if await Ownership.exists(user=user, place=place):
        raise HTTPException(
            status_code=400, detail="User is already an owner of the place"
        )

    # Create a new ownership record
    ownership = await Ownership.create(user=user, place=place)

    return {
        "message": f"User {user_id} added as an owner to place {place_id}",
        "ownership_id": ownership.id,
    }


@club_router.post("/{club_id}/members", tags=["clubs"])
async def add_club_member(
    club_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Add a member to a club."""
    user = await User.get_or_none(id=user_id)
    club = await Club.get_or_none(id=club_id)

    # Check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the club exists
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    # Check if the user is already a member of the club
    if await Membership.exists(user=user, club=club):
        raise HTTPException(
            status_code=400, detail="User is already a member of the club"
        )

    # Create a new membership record
    membership = await Membership.create(user=user, club=club)

    return {
        "message": f"User {user_id} added as a member to club {club_id}",
        "membership_id": membership.id,
    }


@club_router.post("", tags=["clubs"])
async def create_club(
    club_in: ClubIn,
    current_user: User = Depends(get_current_active_user),
):
    """Create a club."""
    club = await Club.create(**club_in.to_dict())
    await Membership.create(club=club, user=current_user, is_admin=True)

    return {
        "message": "Club created successfully.",
        "club": club,
    }


@place_router.post("", tags=["places"])
async def create_place(
    place_in: PlaceIn,
    current_user: User = Depends(get_current_active_user),
):
    """Create a place."""
    place = await Place.create(**place_in.to_dict())
    await place.owners.add(current_user)

    return {
        "message": "Place created successfully.",
        "place": place,
    }
