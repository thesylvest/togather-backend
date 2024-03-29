from tortoise import fields

from app.core.base.models import BaseCreatedAtModel, LocationModel, BaseDBModel, MediaModel


class Event(BaseDBModel, BaseCreatedAtModel, LocationModel, MediaModel):
    class Meta:
        table = "events"

    class PydanticMeta:
        backward_relations = False
        exclude = ["attendees"]
        computed = ["media"]
    name = fields.CharField(max_length=255, unique=True)
    description = fields.TextField()
    links = fields.JSONField(null=True)
    form = fields.JSONField(null=True)
    start_date = fields.DatetimeField(use_tz=True)
    end_date = fields.DatetimeField(use_tz=True)

    host_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="hosted_events", null=True
    )
    host_club: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Club", related_name="hosted_events", null=True
    )
    category: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Category", related_name="events"
    )
    attendees: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="attended_events", backward_key="event_id", through="attendees"
    )

    async def is_host(self, user) -> bool:
        await self.fetch_related("host_club")
        if self.host_club:
            status = await self.host_club.membership_status(user)
            return status == 1
        return self.host_user_id == user.id

    async def can_post(self, user) -> bool:
        try:
            return await self.is_host(user) or (await Attendee.get(event=self, user=user)).is_verified
        except Exception:
            return False

    async def can_rate(self, user) -> bool:
        try:
            return (await Attendee.get(event=self, user=user)).is_verified
        except Exception:
            return False


class Attendee(BaseDBModel):
    class Meta:
        table = "attendees"

    class PydanticMeta:
        backward_relations = False
        exclude = ["form_data"]
    is_verified = fields.BooleanField(default=False)
    form_data = fields.JSONField(null=True)
    event: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Event", related_name="attendance"
    )
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="attendance"
    )
