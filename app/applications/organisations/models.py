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


class Club(Organisation):
    class Meta:
        table = "clubs"
    links = fields.JSONField()
    post_policy = fields.BooleanField(default=True)

    posts: fields.ReverseRelation["models.Post"]
    hosted_events: fields.ReverseRelation["models.Event"]

    members: fields.ManyToManyRelation["models.User"] = fields.ManyToManyField(
        "models.User", related_name="clubs", through="membership"
    )


class Membership(BaseDBModel):
    class Meta:
        table = "members"
    is_admin = fields.BooleanField(default=False)

    club: fields.ForeignKeyRelation["models.Club"] = fields.ForeignKeyField(
        "models.Club", related_name="membership"
    )
    user: fields.ForeignKeyRelation["models.User"] = fields.ForeignKeyField(
        "models.User", related_name="membership"
    )


class Place(Organisation):
    class Meta:
        table = "places"
    is_valid = fields.BooleanField()

    advertisement: fields.ReverseRelation["models.Advertisement"]

    owners: fields.ManyToManyRelation["models.User"] = fields.ManyToManyField(
        "models.User", related_name="places", through="ownership"
    )


class Advertisement(BaseDBModel, BaseCreatedUpdatedAtModel):
    class Meta:
        table = "advertisements"
    description = fields.CharField(max_length=255, null=True)
    picture = fields.CharField(max_length=255, null=True)

    place: fields.ForeignKeyRelation["models.Place"] = fields.ForeignKeyField(
        "models.Place", related_name="advertisements"
    )
