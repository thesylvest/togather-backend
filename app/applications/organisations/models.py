from tortoise import fields

from app.core.base.models import BaseCreatedUpdatedAtModel, LocationModel, BaseDBModel, MediaModel


class Organisation(BaseDBModel, BaseCreatedUpdatedAtModel, LocationModel, MediaModel):
    class Meta:
        abstract = True

    name = fields.CharField(max_length=255, unique=True)
    description = fields.CharField(max_length=255, null=True)
    links = fields.JSONField(null=True)


class Membership(BaseDBModel):
    class Meta:
        table = "memberships"

    is_admin = fields.BooleanField(default=False)

    club: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Club", related_name="memberships", on_delete=fields.CASCADE
    )
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="memberships", on_delete=fields.CASCADE
    )


class Club(Organisation):
    class Meta:
        table = "clubs"

    class PydanticMeta:
        backward_relations = False
        exclude = [
            "members",
            "memberships"
        ]
        computed = ["media"]
    post_policy = fields.BooleanField(default=True)

    posts: fields.ReverseRelation
    hosted_events: fields.ReverseRelation

    category: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Category", related_name="clubs", null=True, on_delete=fields.SET_NULL
    )
    members: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="clubs", backward_key="club_id", through="memberships"
    )

    async def membership_status(self, user):
        membership: Membership = await Membership.get_or_none(club=self, user=user)
        return -1 if membership is None else int(membership.is_admin)

    async def is_admin(self, user):
        membership: Membership = await Membership.get_or_none(club=self, user=user)
        return False if membership is None else membership.is_admin

    async def can_post(self, user):
        if self.post_policy:
            return True
        return await self.is_admin(user)

    async def destroy_non_admin(self):
        if not await Membership.filter(club=self, is_admin=True).exists():
            await self.delete()


class Place(Organisation):
    class Meta:
        table = "places"

    class PydanticMeta:
        backward_relations = False
        exclude = ["owners"]
        computed = ["media"]
    is_valid = fields.BooleanField(default=False)

    advertisements: fields.ReverseRelation

    category: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Category", related_name="places", null=True, on_delete=fields.SET_NULL
    )
    owners: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="places", backward_key="place_id", through="ownerships"
    )

    async def is_owner(self, user):
        return await self.owners.filter(id=user.id).exists()

    async def destroy_non_owner(self):
        if not await self.owners.all().exists():
            await self.delete()


class Advertisement(BaseDBModel, BaseCreatedUpdatedAtModel, MediaModel):
    class Meta:
        table = "advertisements"

    class PydanticMeta:
        exclude = ["place"]
    description = fields.CharField(max_length=255, null=True)

    place: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Place", related_name="advertisements", on_delete=fields.CASCADE
    )
