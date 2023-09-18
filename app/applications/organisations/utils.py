from tortoise.expressions import Subquery, Q
from typing import Optional

from app.applications.interactions.models import Tag
from app.core.base.filter_set import FilterSet
from .models import Club, Place, Membership


class ClubFilter(FilterSet):
    model = Club
    search_fields = ["name", "description"]

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        posts: Optional[int] = None
        hosted_events: Optional[int] = None
        latitude__lte: Optional[float] = None
        latitude__gte: Optional[float] = None
        longitude__lte: Optional[float] = None
        longitude__gte: Optional[float] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        admins: Optional[int] = None
        members: Optional[int] = None
        can_post: Optional[int] = None
        tags: Optional[str] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Club", name__in=tags).values("item_id"))
            ), []

        @staticmethod
        def members(value: int, queryset, user):
            return queryset.filter(memberships__user_id=value, memberships__is_admin=False), []

        @staticmethod
        def admins(value: int, queryset, user):
            return queryset.filter(memberships__user_id=value, memberships__is_admin=True), []

        @staticmethod
        def can_post(value: int, queryset, user):
            return queryset.filter(
                Q(post_policy=True) | Q(id__in=Subquery(Membership.filter(user_id=value, is_admin=True).values("club_id")))
            ), []


class PlaceFilter(FilterSet):
    model = Place
    search_fields = ["name", "description"]

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        owners: Optional[int] = None
        latitude__lte: Optional[float] = None
        latitude__gte: Optional[float] = None
        longitude__lte: Optional[float] = None
        longitude__gte: Optional[float] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        tags: Optional[str] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Place", name__in=tags).values("item_id"))
            ), []
