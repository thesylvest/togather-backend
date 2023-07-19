from typing import Optional

from tortoise import fields
from tortoise.exceptions import DoesNotExist

from app.core.base.base_models import (
    BaseCreatedUpdatedAtModel,
    UUIDDBModel,
    BaseDBModel,
)

from app.applications.users.models import User
from app.applications.events.models import Tag

class Post(BaseDBModel, BaseCreatedUpdatedAtModel, UUIDDBModel):
    is_anon = fields.BooleanField(default=False)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    author_user = fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="posts", null=True
    )
    author_club = fields.ForeignKeyRelation[Club] = fields.ForeignKeyField(
        "models.Club", related_name="posts", null=True
    )
    date = fields.DatetimeField(auto_now_add=True)
    media = fields.JSONField(null=True)
    location = fields.JSONField(null=True)
    comments = fields.ReverseRelation["Comment"]
    tags = fields.ManyToManyRelation[Tag] = fields.ManyToManyField(
        "models.Tag", related_name="posts", through="post_tag"
    )

    class Meta:
        table = "posts"


class Comment(BaseDBModel, BaseCreatedUpdatedAtModel, UUIDDBModel):
    is_anon = fields.BooleanField(default=False)
    content = fields.TextField()
    author = fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="comments"
    )
    post = fields.ForeignKeyRelation[Post] = fields.ForeignKeyField(
        "models.Post", related_name="comments"
    )
    date = fields.DatetimeField(auto_now_add=True)
    media = fields.JSONField(null=True)
    location = fields.JSONField(null=True)
    comments = fields.ReverseRelation["Comment"]
    reply_to = fields.ForeignKeyRelation["Comment"] = fields.ForeignKeyField(
        "models.Comment", related_name="comments", null=True
    )

    class Meta:
        table = "comments"
