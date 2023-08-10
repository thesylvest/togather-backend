from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from app.applications.organisations.models import Club, Place, Membership, Advertisement, Ownership
from app.applications.organisations.schemas import ClubOut, PlaceOut, ClubIn, PlaceIn, AdvertisementIn
from app.applications.users.models import User
from app.applications.users.schemas import UserOut
from app.core.auth.utils.contrib import get_current_active_user
from app.core.base.paginator import paginate


router = APIRouter()


@router.get("/clubs")
async def get_clubs(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all clubs."""
    clubs = Club.all()
    return await paginate(clubs, page, page_size, request, ClubOut, current_user)


@router.get("/places")
async def get_places(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),
):
    """Get all clubs."""
    places = Place.all()
    return await paginate(places, page, page_size, request, PlaceOut, current_user)


@router.get("/clubs/{club_id}")
async def get_club(
    club_id: int,
    current_user: User = Depends(get_current_active_user),
    response_model=ClubOut,
):
    """Get a club."""
    club = await Club.get_or_none(id=club_id).values()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    out = ClubOut(**club)

    return out


@router.get("/places/{place_id}")
async def get_place(
    place_id: int,
    current_user: User = Depends(get_current_active_user),
    response_model=PlaceOut,
):
    """Get a place."""
    place = await Place.get_or_none(id=place_id).values()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    out = PlaceOut(**place)

    return out


@router.get("/clubs/{club_id}/members")
async def get_club_members(
    club_id: int,
    current_user: User = Depends(get_current_active_user),
    response_model=List[UserOut],
):
    """Get all members of a club."""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    memberships = await club.memberships.all().prefetch_related("user")

    out = []
    for membership in memberships:
        member = membership.user

        out.append(
            UserOut(
                id=member.id,
                first_name=member.first_name,
                last_name=member.last_name,
                username=member.username,
                email=member.email,
                bio=member.bio,
                created_at=member.created_at,
            )
        )

    return out


@router.get("/clubs/{club_id}/admins")
async def get_club_admins(
    club_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Get all admins of a club."""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    users = (
        await User.filter(
            memberships__club_id=club_id,
            memberships__is_admin=True,
        )
        .distinct()
        .prefetch_related("memberships")
    )

    out = []

    for user in users:
        out.append(
            UserOut(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
                bio=user.bio,
                created_at=user.created_at,
            )
        )

    return out


@router.post("/clubs/{club_id}/admins/{user_id}")
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


@router.get("/places/{place_id}/ads")
async def get_place_ads(
    place_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Get all ads of a place."""
    place = await Place.get_or_none(id=place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return await place.advertisements.all()


@router.post("/places/{place_id}/ads")
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


@router.get("/places/{place_id}/owners")
async def get_place_owners(
    place_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Get all owners of a place."""
    place = await Place.get_or_none(id=place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    owners = await User.filter(ownerships__place_id=place_id).distinct().prefetch_related("ownerships")

    out = []

    for owner in owners:
        out.append(
            UserOut(
                id=owner.id,
                first_name=owner.first_name,
                last_name=owner.last_name,
                username=owner.username,
                email=owner.email,
                bio=owner.bio,
                created_at=owner.created_at,
            )
        )

    return out


@router.post("/places/{place_id}/owners/{user_id}")
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



@router.post("/clubs/{club_id}/members")
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


@router.post("/clubs")
async def create_club(
    club_in: ClubIn,
    current_user: User = Depends(get_current_active_user),
):
    """Create a club."""
    club = await Club.create(**club_in.to_dict())

    return {
        "message": "Club created successfully.",
        "club": club,
    }


@router.post("/places")
async def create_place(
    place_in: PlaceIn,
    current_user: User = Depends(get_current_active_user),
):
    """Create a place."""
    place = await Place.create(**place_in.to_dict())

    return {
        "message": "Place created successfully.",
        "place": place,
    }
