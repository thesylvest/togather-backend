from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.expressions import Subquery
from pydantic import BaseModel, Field
from tortoise.functions import Avg
from typing import Optional

from app.applications.interactions.models import Tag, Rate
from app.applications.events.models import Attendee
from app.core.base.schemas import BaseOutSchema
from .models import Club, Place, Advertisement


class ClubOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Club)

    @staticmethod
    async def rate(item: Club):
        event_ids = [event.id for event in item.hosted_events]
        return (await Rate.filter(
            item_id__in=event_ids, item_type="Club"
        ).annotate(avg=Avg("rate")).values("avg"))[0]["avg"]

    @staticmethod
    async def tags(item: Club):
        return await Tag.filter(
            item_type=Tag.ModelType.club,
            item_id=item.id
        ).values_list("name", flat=True)

    @classmethod
    async def allowed_actions(cls, item: Club, user):
        is_admin = await item.is_admin(user)
        return {
            "canHide": user is not None,
            "canUpdate": user is not None and is_admin,
            "canDelete": False,
            "canPost": user is not None and await item.can_post(user),
            "canEvent": user is not None and is_admin,
            "canModerate": user is not None and is_admin,
            "canReport": user is not None,
        }

    @classmethod
    async def add_fields(cls, item: Club, user):
        item = await Club.annotate(
            post_count=Subquery(item.posts.all().count()),
            event_attendee_count=Subquery(Attendee.filter(event__host_club=item).count()),
            member_count=Subquery(item.members.all().count()),
        ).prefetch_related("hosted_events").get(id=item.id)
        return {
            "requets_data": {
                "allowed_actions": await ClubOut.allowed_actions(item, user),
            },
            "tags": await ClubOut.tags(item),
            "rate": await ClubOut.rate(item),
            "post_count": item.post_count,
            "hosted_event_count": len(item.hosted_events),
            "member_count": item.member_count,
            "event_attendee_count": item.event_attendee_count,
        }


class PlaceOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Place, exclude=("ownerships", ))

    @staticmethod
    async def tags(item: Place):
        return await Tag.filter(
            item_type=Tag.ModelType.place,
            item_id=item.id
        ).values_list("name", flat=True)

    @classmethod
    async def allowed_actions(cls, item: Place, user):
        is_owner = await item.is_owner(user)
        return {
            "canHide": user is not None,
            "canUpdate": user is not None and is_owner,
            "canDelete": False,
            "canAdvertise": user is not None and is_owner,
            "canReport": user is not None,
        }

    @classmethod
    async def add_fields(cls, item: Place, user):
        item = await Place.annotate(
            owner_count=Subquery(item.owners.all().count()),
            advertisement_count=Subquery(item.advertisements.all().count())
        ).get(id=item.id)
        return {
            "requets_data": {
                "allowed_actions": await PlaceOut.allowed_actions(item, user),
            },
            "owner_count": item.owner_count,
            "advertisement_count": item.advertisement_count,
            "tags": await PlaceOut.tags(item)
        }


class AdvertisementOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Advertisement)


class OrganisationUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    links: Optional[dict] = None
    media: list[dict] = Field(None, max_length=5)
    tags: Optional[list[str]] = []


class OrganisationCreate(OrganisationUpdate):
    name: str
    latitude: float
    longitude: float
    category_id: int


class ClubUpdate(OrganisationUpdate):
    post_policy: Optional[bool] = None


class ClubCreate(OrganisationCreate, ClubUpdate):
    pass


class PlaceUpdate(OrganisationUpdate):
    pass


class PlaceCreate(OrganisationCreate):
    pass


class AdvertisementCreate(BaseModel):
    description: Optional[str] = None
    media: list[dict] = Field(None, max_length=1)
