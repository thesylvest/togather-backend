from typing import Optional

from tortoise import fields
from tortoise.exceptions import DoesNotExist

from app.core.base.base_models import (
    BaseCreatedAtModel,
    BaseCreatedUpdatedAtModel,
    UUIDDBModel,
    BaseDBModel,
)
from app.applications.posts.models import Post

class Event(BaseDBModel, BaseCreatedAtModel, UUIDDBModel):
    name = fields.CharField(max_length=255)
    host_user = fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="hosted_events", null=True
    )
    host_club = fields.ForeignKeyRelation["Club"] = fields.ForeignKeyField(
        "models.Club", related_name="hosted_events", null=True
    )
    description = fields.TextField()
    picture = fields.JSONField(null=True)
    links = fields.JSONField(null=True)
    # TODO: form
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    location = fields.JSONField(null=True)
    media = fields.JSONField(null=True)
    rate = fields.FloatField(default=0)
    qr_code = fields.JSONField(null=True)
    verification_link = fields.CharField(max_length=255, null=True)
    responses = fields.ReverseRelation["FormResponse"]
    category = fields.ForeignKeyRelation["Category"] = fields.ForeignKeyField(
        "models.Category", related_name="events", null=True
    )
    tags = fields.ManyToManyRelation["Tag"] = fields.ManyToManyField(
        "models.Tag", related_name="events", through="event_tag"
    )

    class Meta:
        table = "events"

class FormResponse(BaseDBModel, BaseCreatedUpdatedAtModel, UUIDDBModel):
    data = fields.JSONField()
    event = fields.ForeignKeyRelation[Event] = fields.ForeignKeyField(
        "models.Event", related_name="responses"
    )
    user = fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="form_responses"
    )

    class Meta:
        table = "form_responses"

class Category(BaseDBModel, UUIDDBModel):
    name = fields.CharField(max_length=255)
    picture = fields.JSONField(null=True)
    events = fields.ReverseRelation[Event]

class Tag(BaseDBModel, UUIDDBModel):
    name = fields.CharField(max_length=255)
    events = fields.ManyToManyRelation[Event] = fields.ManyToManyField(
        "models.Event", related_name="tags", through="event_tag"
    )
    posts = fields.ManyToManyRelation[Post] = fields.ManyToManyField(
        "models.Post", related_name="tags", through="post_tag"
    )