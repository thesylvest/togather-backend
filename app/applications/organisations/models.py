from tortoise import fields

from app.core.base.models import (
    BaseCreatedUpdatedAtModel,
    LocationModel,
    BaseDBModel,
)


class Organisation(BaseDBModel, BaseCreatedUpdatedAtModel, LocationModel):
    class Meta:
        abstract = True

    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255, null=True)
    picture = fields.CharField(max_length=255, null=True)
    banner = fields.CharField(max_length=255, null=True)


class Membership(BaseDBModel):
    class Meta:
        table = "memberships"

    is_admin = fields.BooleanField(default=False)

    club: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Club", related_name="memberships"
    )
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="memberships"
    )


class Club(Organisation):
    class Meta:
        table = "clubs"

    links = fields.JSONField(null=True)
    post_policy = fields.BooleanField(default=True)

    posts: fields.ReverseRelation
    hosted_events: fields.ReverseRelation

    members: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="clubs", backward_key="club_id", through="memberships"
    )

    async def membership_status(self, user):
        membership: Membership = await Membership.get_or_none(club=self, user=user)
        return -1 if membership is None else int(membership.is_admin)


class Place(Organisation):
    class Meta:
        table = "places"

    is_valid = fields.BooleanField(default=False)

    advertisements: fields.ReverseRelation

    owners: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="places", backward_key="place_id", through="ownerships"
    )


class Advertisement(BaseDBModel, BaseCreatedUpdatedAtModel):
    class Meta:
        table = "advertisements"

    description = fields.CharField(max_length=255, null=True)
    picture = fields.CharField(max_length=255, null=True)

    place: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Place", related_name="advertisements"
    )


class Ownership(BaseDBModel):
    class Meta:
        table = "ownerships"

    place: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Place", related_name="ownerships"
    )
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="ownerships"
    )
