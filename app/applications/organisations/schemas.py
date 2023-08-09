from typing import Optional
from pydantic import BaseModel
from app.core.base.schemas import BaseOutSchema


class BaseOrganisationOut(BaseOutSchema):
    id: int
    name: str
    description: Optional[str] = None
    picture: Optional[str] = None
    banner: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @classmethod
    def add_fields(cls, item, user):  # TODO: modify actions related to connections
        if item == user:
            allowed_actions = ["edit"]
        else:
            allowed_actions = ["connect", "block", "hide"]

        return {"allowed_actions": allowed_actions}


class ClubIn(BaseOutSchema):
    name: str
    description: Optional[str] = None
    picture: Optional[str] = None
    banner: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    links: Optional[dict] = None
    post_policy: Optional[bool] = None

    @classmethod
    def add_fields(cls, item, user):  # TODO: modify actions related to connections
        if item == user:
            allowed_actions = ["edit"]
        else:
            allowed_actions = ["connect", "block", "hide"]

        return {"allowed_actions": allowed_actions}


class ClubOut(BaseOrganisationOut):
    links: Optional[dict] = None
    post_policy: Optional[bool] = None


class PlaceOut(BaseOrganisationOut):
    is_valid: Optional[bool] = None
