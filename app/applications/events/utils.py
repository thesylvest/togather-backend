from tortoise.expressions import Subquery, Q
from datetime import datetime
from typing import Optional

from app.applications.interactions.models import Tag
from app.applications.users.models import Blocked
from app.core.base.filter_set import FilterSet
from .models import Event, Attendee


class EventFilter(FilterSet):
    model = Event
    search_fields = ["name", "description"]

    @classmethod
    def block(cls, user):
        return Q(host_user_id__in=Subquery(Blocked.filter(blocking_user=user).values("blocked_user_id")))

    class Parameters(FilterSet.Parameters):
        host_club: Optional[int] = None
        host_user: Optional[int] = None
        attendees: Optional[int] = None
        category: Optional[int] = None
        start_date__gte: Optional[datetime] = None
        end_date__lte: Optional[datetime] = None
        latitude__lte: Optional[float] = None
        latitude__gte: Optional[float] = None
        longitude__lte: Optional[float] = None
        longitude__gte: Optional[float] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        has_club: Optional[int] = None
        tags: Optional[str] = None
        verified_attendees: Optional[int] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def tags(value: str, queryset, user):
            tags = value.split(",")
            return queryset.filter(
                id__in=Subquery(Tag.filter(item_type="Event", name__in=tags).values("item_id"))
            ), []

        @staticmethod
        def has_club(value: int, queryset, user):
            if value == 1:
                return queryset.filter(host_club=None), []
            return queryset.exclude(host_club=None), []

        @staticmethod
        def verified_attendees(value: int, queryset, user):
            return queryset.filter(id__in=Subquery(Attendee.filter(user_id=value, is_verified=True).values("event_id"))), []


class AttendeeFilter(FilterSet):
    model = Attendee
    search_fields = ["user__username", "event__name"]

    class Parameters(FilterSet.Parameters):
        event: Optional[int] = None
        user: Optional[int] = None
