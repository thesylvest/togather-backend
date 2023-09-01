from tortoise.expressions import Subquery, Q
from typing import Optional

from app.applications.interactions.models import Tag
from app.applications.users.models import Blocked
from app.core.base.filter_set import FilterSet
from .models import Post, Comment


class PostFilter(FilterSet):
    model = Post

    @classmethod
    def mode_filters(cls, user):
        hidden, _ = super().mode_filters(user)
        blocked = Q(creator_id__in=Subquery(Blocked.filter(blocking_user=user).values("blocked_user_id")))
        return hidden, blocked

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        creator: Optional[int] = None
        author_club: Optional[int] = None

    class SearchFields(FilterSet.SearchFields):
        title: str
        content: str

    class FunctionFilters(FilterSet.FunctionFilters):
        tags: Optional[str] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Place", name__in=tags).values("item_id"))
            ), []


class CommentFilter(FilterSet):
    model = Comment

    @classmethod
    def mode_filters(cls, user):
        hidden, _ = super().mode_filters(user)
        blocked = Q(creator__in=Subquery(user.blocked_users.all()))
        return hidden, blocked

    class Parameters(FilterSet.Parameters):
        creator: Optional[int] = None
        post: Optional[int] = None
        reply_to: Optional[int] = None

    class SearchFields(FilterSet.SearchFields):
        content: str

    class FunctionFilters(FilterSet.FunctionFilters):
        tags: Optional[str] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Place", name__in=tags).values("item_id"))
            ), []
