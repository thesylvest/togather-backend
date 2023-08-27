from typing import Optional

from app.core.base.filter_set import FilterSet
from .models import Hide


class HideFilter(FilterSet):
    model = Hide

    class Parameters(FilterSet.Parameters):
        item_type: Optional[str] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        me: str = "me"

    class Functions(FilterSet.Functions):
        @staticmethod
        def me(value: int, queryset, user):
            return queryset.filter(hider=user)
