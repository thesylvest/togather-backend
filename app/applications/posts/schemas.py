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
            "can_hide": user is not None,
            "can_update": user is not None and is_creator,
            "can_delete": user is not None and is_creator,
            "can_report": user is not None,
        }

    @classmethod
    async def add_fields(cls, item: Post, user):
        item = await Post.annotate(
            comment_count=Subquery(item.comments.all().count()),
            rate_count=Subquery(Rate.filter(item_id=item.id, item_type="Post").count())
        ).prefetch_related("creator", "author_club").get(id=item.id)
        user_rate = await Rate.get_or_none(item_id=item.id, item_type="Post")
        return {
            "request_data": {
                "allowed_actions": await PostOut.allowed_actions(item, user),
                "user_rate": user_rate.rate if user_rate else None
            },
            "tags": await PostOut.tags(item),
            "rate": await PostOut.rate(item),
            "comment_count": item.comment_count,
            "rate_count": item.rate_count,
            "author_user": await UserOut.serialize(item.creator, user) if not item.is_anon else None
        }


class CommentOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Comment)

    @staticmethod
    async def rate(item: Comment):
        return (await Rate.filter(
            item_id=item.id, item_type="Comment"
        ).annotate(avg=Avg("rate")).values("avg"))[0]["avg"]

    @classmethod
    async def allowed_actions(cls, item: Comment, user):
        is_creator = (user is not None) and (item.creator_id == user.id)
        return {
            "can_hide": user is not None,
            "can_update": user is not None and is_creator,
            "can_delete": user is not None and is_creator,
            "can_report": user is not None,
        }

    @classmethod
    async def add_fields(cls, item: Comment, user):
        item = await Comment.annotate(
            reply_count=Subquery(item.comments.all().count()),
            rate_count=Subquery(Rate.filter(item_id=item.id, item_type="Comment").count())
        ).prefetch_related("creator").get(id=item.id)
        user_rate = await Rate.get_or_none(item_id=item.id, item_type="Comment")
        return {
            "requets_data": {
                "allowed_actions": await CommentOut.allowed_actions(item, user),
                "user_rate": user_rate.rate if user_rate else None
            },
            "rate": await CommentOut.rate(item),
            "rate_count": item.rate_count,
            "reply_count": item.reply_count,
            "author_user": await UserOut.pydantic_model.from_tortoise_orm(item.creator) if not item.is_anon else None
        }


class PostUpdate(BaseModel):
    is_anon: Optional[bool] = None
    content: Optional[str] = None
    title: Optional[str] = None
    media: list[dict] = Field(None, max_length=5)
    tags: Optional[list[str]] = []


class PostCreate(PostUpdate):
    author_club_id: Optional[int] = None
    event_id: Optional[int] = None
    content: str
    title: str
    latitude: Optional[float]
    longitude: Optional[float]


class CommentUpdate(BaseModel):
    is_anon: Optional[bool] = None
    content: Optional[str] = None


class CommentCreate(CommentUpdate):
    is_anon: bool
    content: str
    post_id: int
    reply_to_id: Optional[int] = None
