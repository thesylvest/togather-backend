from tortoise import fields

from app.core.base.models import BaseCreatedUpdatedAtModel, LocationModel, BaseDBModel, MediaModel


class Post(BaseDBModel, BaseCreatedUpdatedAtModel, LocationModel, MediaModel):
    class Meta:
        table = "posts"

    class PydanticMeta:
        backward_relations = False
        exclude = ["creator", "creator_id"]
        computed = ["media"]
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    posted_by_admin = fields.BooleanField(default=False)
    is_anon = fields.BooleanField(default=False)

    comments: fields.ReverseRelation

    creator: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", null=True, related_name="posts"
    )
    author_club: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Club", related_name="posts", null=True
    )
    event: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Event", related_name="posts", null=True
    )

    async def is_creator(self, user):
        if self.author_club:
            return (self.creator == user and self.author_club.post_policy) or await self.author_club.is_admin(user)
        return self.creator == user


class Comment(BaseDBModel, BaseCreatedUpdatedAtModel):
    class Meta:
        table = "comments"

    class PydanticMeta:
        backward_relations = False
        exclude = ["creator", "post", "reply_to", "creator_id"]
    content = fields.TextField()
    is_anon = fields.BooleanField(default=False)

    comments: fields.ReverseRelation

    creator: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", null=True, related_name="comments"
    )
    post: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Post", related_name="comments"
    )
    reply_to: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Comment", related_name="comments", null=True
    )

    async def is_creator(self, user):
        return self.creator == user
