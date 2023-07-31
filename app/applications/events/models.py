from tortoise import fields

from app.core.base.models import (
    BaseCreatedAtModel,
    LocationModel,
    BaseDBModel,
)


class Event(BaseDBModel, BaseCreatedAtModel, LocationModel):
    class Meta:
        table = "events"
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    picture = fields.CharField(max_length=255, null=True)
    links = fields.JSONField(null=True)
    form = fields.JSONField(null=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    media = fields.JSONField(null=True)
    rate = fields.FloatField(default=0)
    qr_code = fields.JSONField(null=True)
    verification_link = fields.CharField(max_length=255, null=True)

    responses: fields.ReverseRelation["models.FormResponse"]

    host_user: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="hosted_events", null=True
    )
    host_club: fields.ForeignKeyRelation["models.Club"] = fields.ForeignKeyField(
        "models.Club", related_name="hosted_events", null=True
    )
    category: fields.ForeignKeyRelation["models.Category"] = fields.ForeignKeyField(
        "models.Category", related_name="events", null=True
    )


class FormResponse(BaseDBModel, BaseCreatedAtModel):
    class Meta:
        table = "form_responses"
    data = fields.JSONField()

    event: fields.ForeignKeyRelation["models.Event"] = fields.ForeignKeyField(
        "models.Event", related_name="responses"
    )
    user: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="form_responses"
    )


class Category(BaseDBModel):
    class Meta:
        table = "categories"
    name = fields.CharField(max_length=255)
    picture = fields.CharField(max_length=255, null=True)

    events = fields.ReverseRelation["models.Event"]
