from typing import Optional

from tortoise import fields
from tortoise.exceptions import DoesNotExist

from app.core.base.base_models import (
    BaseCreatedUpdatedAtModel,
    BaseDBModel,
)

from app.applications.users.models import User
from app.core.base.base_models import Tag


class Post(BaseDBModel, BaseCreatedUpdatedAtModel):
    is_anon = fields.BooleanField(default=False)
    title = fields.CharField(max_length=255)
    media = fields.CharField(max_length=255, null=True)
    content = fields.TextField()
    location = fields.JSONField(null=True)
    comments: fields.ReverseRelation["Comment"]
    author_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="posts", null=True
    )
    author_club: fields.ForeignKeyRelation[Club] = fields.ForeignKeyField(
        "models.Club", related_name="posts", null=True
    )
    tags: fields.ManyToManyRelation[Tag] = fields.ManyToManyField(
        "models.Tag", related_name="posts", through="post_tag"
    )

    class Meta:
        table = "posts"


class Comment(BaseDBModel, BaseCreatedUpdatedAtModel):
    is_anon = fields.BooleanField(default=False)
    content = fields.TextField()
    media = fields.CharField(max_length=255, null=True)
    location = fields.JSONField(null=True)
    comments: fields.ReverseRelation["Comment"]
    author: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="comments"
    )
    post: fields.ForeignKeyRelation[Post] = fields.ForeignKeyField(
        "models.Post", related_name="comments"
    )
    reply_to: fields.ForeignKeyRelation["Comment"] = fields.ForeignKeyField(
        "models.Comment", related_name="comments", null=True
    )

    class Meta:
        table = "comments"
