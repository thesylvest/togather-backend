from tortoise import fields
from app.core.base.base_models import Tag, Category
from app.applications.users.models import User
from app.core.base.base_models import (
    BaseCreatedAtModel,
    BaseDBModel,
)


class Event(BaseDBModel, BaseCreatedAtModel):
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    picture = fields.CharField(max_length=255, null=True)
    links = fields.JSONField(null=True)
    form = fields.JSONField(null=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    location = fields.JSONField(null=True)
    media = fields.JSONField(null=True)
    rate = fields.FloatField(default=0)
    qr_code = fields.JSONField(null=True)
    verification_link = fields.CharField(max_length=255, null=True)
    responses: fields.ReverseRelation["FormResponse"]
    host_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="hosted_events", null=True
    )
    host_club: fields.ForeignKeyRelation["Club"] = fields.ForeignKeyField(
        "models.Club", related_name="hosted_events", null=True
    )
    category: fields.ForeignKeyRelation[Category] = fields.ForeignKeyField(
        "models.Category", related_name="events", null=True
    )
    tags: fields.ManyToManyRelation[Tag] = fields.ManyToManyField(
        "models.Tag", related_name="events", through="event_tag"
    )

    class Meta:
        table = "events"


class FormResponse(BaseDBModel, BaseCreatedAtModel):
    data = fields.JSONField()
    event: fields.ForeignKeyRelation[Event] = fields.ForeignKeyField(
        "models.Event", related_name="responses"
    )
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="form_responses"
    )

    class Meta:
        table = "form_responses"
