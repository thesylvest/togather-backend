from tortoise.contrib.pydantic import pydantic_model_creator
from typing import Optional

from app.core.base.schemas import BaseOutSchema, BaseInSchema
from .models import Club, Place, Membership


class ClubIn(BaseInSchema):
    name: str
    description: Optional[str] = None
    picture: Optional[str] = None
    banner: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    links: Optional[dict] = None
    post_policy: Optional[bool] = None


class ClubOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Club, exclude=("members", "memberships"))

    @classmethod
    def add_fields(cls, item, user):  # TODO: modify actions related to connections
        if item == user:
            allowed_actions = ["edit"]
        else:
            allowed_actions = ["connect", "block", "hide"]

        return {"allowed_actions": allowed_actions}


class ClubMembersOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Membership, exclude=("club", "club_id", "id"))


class PlaceIn(BaseInSchema):
    name: str
    description: Optional[str] = None
    picture: Optional[str] = None
    banner: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PlaceOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Place, exclude=("ownerships", ))


class AdvertisementIn(BaseInSchema):
    description: Optional[str] = None
    picture: Optional[str] = None
