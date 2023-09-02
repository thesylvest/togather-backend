from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.expressions import Subquery
from pydantic import BaseModel, Field
from tortoise.functions import Avg
from typing import Optional

from app.applications.interactions.models import Tag, Rate
from app.applications.users.schemas import UserOut
from app.core.base.schemas import BaseOutSchema
from .models import Post, Comment


class PostOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Post)

    @staticmethod
    async def rate(item: Post):
        return (await Rate.filter(
            item_id=item.id, item_type="Post"
        ).annotate(avg=Avg("rate")).values("avg"))[0]["avg"]

    @staticmethod
    async def tags(item: Post):
        return await Tag.filter(
            item_type="Post", item_id=item.id
        ).values_list("name", flat=True)

    @classmethod
    async def allowed_actions(cls, item: Post, user):
        is_creator = await item.is_creator(user)
        return {
            "canHide": user is not None,
            "canUpdate": user is not None and is_creator,
            "canDelete": user is not None and is_creator,
            "canReport": user is not None,
        }

    @classmethod
    async def add_fields(cls, item: Post, user):
        item = await Post.annotate(
            comment_count=Subquery(item.comments.all().count()),
        ).prefetch_related("creator").get(id=item.id)
        return {
            "requets_data": {
                "allowed_actions": await PostOut.allowed_actions(item, user),
            },
            "tags": await PostOut.tags(item),
            "rate": await PostOut.rate(item),
            "comment_count": item.comment_count,
            "author_user": await UserOut.pydantic_model.from_tortoise_orm(item.creator) if not item.is_anon else None
        }


class CommentOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Comment)

    @staticmethod
    async def rate(item: Comment):
        return (await Rate.filter(
            item_id=item.id, item_type="Comment"
        ).annotate(avg=Avg("rate")).values("avg"))[0]["avg"]

    @staticmethod
    async def tags(item: Comment):
        return await Tag.filter(
            item_type="Comment", item_id=item.id
        ).values_list("name", flat=True)

    @classmethod
    async def allowed_actions(cls, item: Comment, user):
        is_creator = item.creator_id = user.id
        return {
            "canHide": user is not None,
            "canUpdate": user is not None and is_creator,
            "canDelete": user is not None and is_creator,
            "canReport": user is not None,
        }

    @classmethod
    async def add_fields(cls, item: Comment, user):
        item = await Comment.annotate(
            reply_count=Subquery(item.comments.all().count()),
        ).prefetch_related("creator").get(id=item.id)
        return {
            "requets_data": {
                "allowed_actions": await CommentOut.allowed_actions(item, user),
            },
            "tags": await CommentOut.tags(item),
            "rate": await CommentOut.rate(item),
            "reply_count": item.reply_count,
            "author_user": await UserOut.pydantic_model.from_tortoise_orm(item.creator) if not item.is_anon else None
        }


class PostUpdate(BaseModel):
    is_anon: Optional[bool] = None
    content: Optional[str] = None
    title: Optional[str] = None
    category_id: Optional[int] = None
    media: list[dict] = Field(None, max_length=1)
    tags: Optional[list[str]] = []


class PostCreate(PostUpdate):
    author_club_id: Optional[int] = None
    event_id: Optional[int] = None
    content: str
    title: str
    category_id: int
    latitude: float
    longitude: float


class CommentUpdate(BaseModel):
    is_anon: Optional[bool] = None
    content: Optional[str] = None


class CommentCreate(CommentUpdate):
    is_anon: bool
    content: str
    post_id: int
    reply_to_id: Optional[int] = None
