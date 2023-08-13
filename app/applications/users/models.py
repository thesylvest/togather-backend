from typing import Optional

from tortoise.exceptions import DoesNotExist
from tortoise import fields

from app.core.auth.utils import password
from app.core.base.models import (
    BaseCreatedAtModel,
    LocationModel,
    BaseDBModel,
)


class User(BaseDBModel, BaseCreatedAtModel, LocationModel):
    class Meta:
        table = "users"

    class PydanticMeta:
        backward_relations = False
        exclude = ("password_hash", "clubs", "hosted_events", "place", "notifications", "is_superuser", "is_active")
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

    sent_connections: fields.ReverseRelation
    received_connections: fields.ReverseRelation
    blocked_users: fields.ReverseRelation
    posts: fields.ReverseRelation
    comments: fields.ReverseRelation
    form_responses: fields.ReverseRelation
    reports: fields.ReverseRelation
    hides: fields.ReverseRelation
    devices: fields.ReverseRelation
    hosted_events: fields.ManyToManyRelation
    places: fields.ManyToManyRelation
    notifications: fields.ManyToManyRelation
    clubs: fields.ManyToManyRelation

    university: fields.ForeignKeyRelation = fields.ForeignKeyField(
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
    async def create(cls, user) -> "User":
        user_dict = user.dict()
        password_hash = password.get_password_hash(password=user.password)
        model = cls(**user_dict, password_hash=password_hash)
        await model.save()
        return model


class Connection(BaseDBModel):
    class Meta:
        table = "connections"
    is_accepted = fields.BooleanField(default=False)

    from_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="sent_connections"
    )
    to_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="received_connections"
    )


class Blocked(BaseDBModel):
    class Meta:
        table = "blocked"
    blocking_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User"
    )
    blocked_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="blocked_users"
    )


class University(BaseDBModel, LocationModel):
    class Meta:
        table = "universities"
    name = fields.CharField(max_length=255, unique=True)

    clubs: fields.ReverseRelation
    students: fields.ReverseRelation
    events: fields.ReverseRelation
