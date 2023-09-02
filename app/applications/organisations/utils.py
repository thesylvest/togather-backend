from tortoise.expressions import Subquery
from typing import Optional

from app.applications.interactions.models import Tag
from app.core.base.filter_set import FilterSet
from .models import Club, Place


class ClubFilter(FilterSet):
    model = Club
    search_fields = ["name", "description"]

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        posts: Optional[int] = None
        hosted_events: Optional[int] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        admins: Optional[int] = None
        members: Optional[int] = None
        tags: Optional[str] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Club", name__in=tags).values("item_id"))
            ), []

        @staticmethod
        def admins(value: int, queryset, user):
            return queryset.filter(memberships__user_id=value, memberships__is_admin=True), []

        @staticmethod
        def members(value: int, queryset, user):
            return queryset.filter(memberships__user_id=value, memberships__is_admin=False), []


class PlaceFilter(FilterSet):
    model = Place
    search_fields = ["name", "description"]

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        owners: Optional[int] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        tags: Optional[str] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Place", name__in=tags).values("item_id"))
            ), []
