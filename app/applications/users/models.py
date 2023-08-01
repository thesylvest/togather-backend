from typing import Optional

from tortoise.exceptions import DoesNotExist
from tortoise import fields

from app.core.auth.utils import password
from .schemas import BaseUserCreate
from app.core.base.models import (
    BaseCreatedAtModel,
    LocationModel,
    BaseDBModel,
)


class User(BaseDBModel, BaseCreatedAtModel, LocationModel):
    class Meta:
        table = "users"
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    password_hash = fields.CharField(max_length=60, null=True)
    last_login = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    bio = fields.TextField(null=True)
    gender = fields.CharField(max_length=10, null=True)
    social_links = fields.JSONField(null=True)
    birth_date = fields.DateField(null=True)
    profile_picture = fields.CharField(max_length=255, null=True)
    unread_notifications = fields.IntField(default=0)

    sent_connections: fields.ReverseRelation["models.Connection"]
    received_connections: fields.ReverseRelation["models.Connection"]
    blocked_users: fields.ReverseRelation["models.Blocked"]
    posts: fields.ReverseRelation["models.Post"]
    comments: fields.ReverseRelation["models.Comment"]
    hosted_events: fields.ReverseRelation["models.Event"]
    form_responses: fields.ReverseRelation["models.FormResponse"]
    reports: fields.ReverseRelation["models.Report"]
    hides: fields.ReverseRelation["models.Hide"]
    clubs: fields.ReverseRelation["models.Club"]
    places: fields.ReverseRelation["models.Place"]
    notifications: fields.ReverseRelation["models.Notifications"]
    devices: fields.ReverseRelation["models.FCMDevice"]

    university: fields.ForeignKeyRelation["models.University"] = fields.ForeignKeyField(
        "models.University", related_name="students", null=True
    )

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        try:
            user = await cls.get_or_none(email=email)
            return user
        except DoesNotExist:
            return None

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        try:
            user = await cls.get(username=username)
            return user
        except DoesNotExist:
            return None

    @classmethod
    async def create(cls, user: BaseUserCreate) -> "User":
        user_dict = user.dict()
        password_hash = password.get_password_hash(password=user.password)
        model = cls(**user_dict, password_hash=password_hash)
        await model.save()
        return model


class Connection(BaseDBModel):
    class Meta:
        table = "connections"
    is_accepted = fields.BooleanField(default=False)

    from_user: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="sent_connections"
    )
    to_user: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="received_connections"
    )


class Blocked(BaseDBModel):
    class Meta:
        table = "blocked"
    blocking_user: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User"
    )
    blocked_user: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="blocked_users"
    )


class University(BaseDBModel, LocationModel):
    class Meta:
        table = "universities"
    name = fields.CharField(max_length=255, unique=True)

    clubs: fields.ReverseRelation["models.Club"]
    students: fields.ReverseRelation["models.User"]
    events: fields.ReverseRelation["models.Event"]
