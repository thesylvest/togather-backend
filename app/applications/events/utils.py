from datetime import datetime
from typing import Optional

from app.core.base.filter_set import FilterSet, ListStr
from .models import Event, Attendee


class EventFilter(FilterSet):
    model = Event

    class Parameters(FilterSet.Parameters):
        host_user__id__in: Optional[ListStr] = None
        host_club: Optional[int] = None
        host_user: Optional[int] = None
        attendees: Optional[int] = None
        category: Optional[int] = None
        start_date__gte: Optional[datetime] = None
        end_date__lte: Optional[datetime] = None

    class SearchFields(FilterSet.SearchFields):
        name: str
        description: str

    class FunctionFilters(FilterSet.FunctionFilters):
        has_club: Optional[int] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def has_club(value: int, queryset, user):
            if value == 1:
                return queryset.filter(host_club=None)
            return queryset.exclude(host_club=None)


class AttendeeFilter(FilterSet):
    model = Attendee

    class Parameters(FilterSet.Parameters):
        event_id: Optional[int] = None

    class SearchFields(FilterSet.SearchFields):
        user__username: str
