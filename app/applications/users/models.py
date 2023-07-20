from typing import Optional

from tortoise import fields
from tortoise.exceptions import DoesNotExist

from app.applications.users.schemas import BaseUserCreate
from app.core.base.base_models import (
    BaseCreatedAtModel,
    BaseDBModel,
)
from app.core.auth.utils import password


class User(BaseDBModel, BaseCreatedAtModel):
    username = fields.CharField(max_length=20, unique=True)
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
    location = fields.JSONField(null=True)
    profile_picture = fields.CharField(max_length=255, null=True)
    # TODO: unread_notifications =
    sent_connections: fields.ReverseRelation["Connection"]
    received_connections: fields.ReverseRelation["Connection"]
    blocked_users: fields.ReverseRelation["Blocked"]
    posts: fields.ReverseRelation["Post"]
    comments: fields.ReverseRelation["Comment"]
    form_responses: fields.ReverseRelation["FormResponse"]
    hosted_events: fields.ReverseRelation["Event"]
    university: fields.ForeignKeyRelation["University"] = fields.ForeignKeyField(
        "models.University", related_name="students", null=True
    )
    # TODO: Muti will add clubs field

    def full_name(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.username

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

    class Meta:
        table = "users"

    class PydanticMeta:
        computed = ["full_name"]


class Connection(BaseDBModel):
    is_accepted = fields.BooleanField(default=False)
    from_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="sent_connections"
    )
    to_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="received_connections"
    )

    class Meta:
        table = "connections"


class Blocked(BaseDBModel):
    blocking_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User"
    )
    blocked_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="blocked_users"
    )

    class Meta:
        table = "blocked"


class University(BaseDBModel):
    name = fields.CharField(max_length=255, unique=True)
    location = fields.JSONField(null=True)
    clubs: fields.ReverseRelation["Club"]
    students: fields.ReverseRelation["User"]
    events: fields.ReverseRelation["Event"]

    class Meta:
        table = "universities"
