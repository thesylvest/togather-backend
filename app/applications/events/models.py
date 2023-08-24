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

    responses: fields.ReverseRelation

    host_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="hosted_events", null=True
    )
    host_club: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Club", related_name="hosted_events", null=True
    )
    category: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Category", related_name="events", null=True
    )
    attendees: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="attended_events"
    )

    async def is_host(self, user) -> bool:
        if self.host_club:
            status = await self.host_club.membership_status(user)
            return status == 1
        return self.host_user == user


class FormResponse(BaseDBModel, BaseCreatedAtModel):
    class Meta:
        table = "form_responses"
    data = fields.JSONField()

    event: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Event", related_name="responses"
    )
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="form_responses"
    )
