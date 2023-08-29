from typing import Optional

from app.core.base.filter_set import FilterSet
from .models import Club, Place


class ClubFilter(FilterSet):
    model = Club

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        posts: Optional[int] = None
        hosted_events: Optional[int] = None

    class SearchFields(FilterSet.SearchFields):
        name: str
        description: str

    class FunctionFilters(FilterSet.FunctionFilters):
        admins: Optional[int] = None
        members: Optional[int] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def admins(value: int, queryset, user):
            return queryset.filter(memberships__user_id=value, memberships__is_admin=True)

        @staticmethod
        def members(value: int, queryset, user):
            return queryset.filter(memberships__user_id=value, memberships__is_admin=False)


class PlaceFilter(FilterSet):
    model = Place

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        owners: Optional[int] = None

    class SearchFields(FilterSet.SearchFields):
        name: str
        description: str
