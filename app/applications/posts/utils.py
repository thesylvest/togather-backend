from tortoise.expressions import Subquery, Q
from typing import Optional

from app.applications.interactions.models import Tag
from app.applications.users.models import Blocked
from app.core.base.filter_set import FilterSet
from .models import Post, Comment


class PostFilter(FilterSet):
    model = Post
    search_fields = ["title", "content"]

    @classmethod
    def block(cls, user):
        return Q(creator_id__in=Subquery(Blocked.filter(blocking_user=user).values("blocked_user_id")))

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        author_club: Optional[int] = None
        event: Optional[int] = None
        latitude__lte: Optional[float] = None
        latitude__gte: Optional[float] = None
        longitude__lte: Optional[float] = None
        longitude__gte: Optional[float] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        creator: Optional[int] = None
        tags: Optional[str] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def creator(value: str, queryset, user):
            return queryset.filter(creator_id=value, is_anon=False), []

        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Place", name__in=tags).values("item_id"))
            ), []


class CommentFilter(FilterSet):
    model = Comment
    search_fields = ["content"]

    @classmethod
    def block(cls, user):
        return Q(creator_id__in=Subquery(Blocked.filter(blocking_user=user).values("blocked_user_id")))

    class Parameters(FilterSet.Parameters):
        creator: Optional[int] = None
        reply_to: Optional[int] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        tags: Optional[str] = None
        post: Optional[int] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Place", name__in=tags).values("item_id"))
            ), []

        @staticmethod
        def post(value: int, queryset, user):
            return queryset.filter(post_id=value, reply_to_id=None), []
