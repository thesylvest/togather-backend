from tortoise.expressions import Q, Subquery
from tortoise.functions import Sum
from datetime import datetime
from typing import Optional

from app.core.base.filter_set import FilterSet
from .models import User, Connection, Blocked


async def update_last_login(user_id: int) -> None:
    user = await User.get(id=user_id)
    user.last_login = datetime.now()
    await user.save()


class UserFilter(FilterSet):
    model = User
    search_fields = ["username", "first_name", "last_name", "bio"]

    @classmethod
    def block(cls, user):
        return Q(id__in=Subquery(Blocked.filter(blocking_user=user).values("blocked_user_id")))

    class Parameters(FilterSet.Parameters):
        posts: Optional[int] = None
        comments: Optional[int] = None
        hosted_events: Optional[int] = None
        attended_events: Optional[int] = None
        places: Optional[int] = None
        clubs: Optional[int] = None
        latitude__lte: Optional[float] = None
        latitude__gte: Optional[float] = None
        longitude__lte: Optional[float] = None
        longitude__gte: Optional[float] = None

    class FunctionFilters(FilterSet.FunctionFilters):
        connections: Optional[int] = None
        rated_post: Optional[int] = None
        rated_comment: Optional[int] = None
        rated_event: Optional[int] = None
        club_admins: Optional[int] = None
        club_members: Optional[int] = None
        verified_attendees: Optional[int] = None
        unverified_attendees: Optional[int] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def connections(value: int, queryset, user):
            return queryset.filter(
                Q(id__in=Subquery(Connection.filter(is_accepted=True, from_user_id=value).values('to_user_id'))) |
                Q(id__in=Subquery(Connection.filter(is_accepted=True, to_user_id=value).values('from_user_id')))
            ), []

        @staticmethod
        def club_admins(value: int, queryset, user):
            return queryset.filter(memberships__club_id=value, memberships__is_admin=True), []

        @staticmethod
        def club_members(value: int, queryset, user):
            return queryset.filter(memberships__club_id=value, memberships__is_admin=False), []

        @staticmethod
        def verified_attendees(value: int, queryset, user):
            return queryset.filter(attendance__event_id=value, attendance__is_verified=True), []

        @staticmethod
        def unverified_attendees(value: int, queryset, user):
            return queryset.filter(attendance__event_id=value, attendance__is_verified=False), []

        @staticmethod
        def rated_post(value: int, queryset, user):
            return queryset.filter(rates__item_type="Post", rates__item_id=value).annotate(
                rate=Sum("rates__rate", _filter=Q(rates__item_type="Post", rates__item_id=value))
            ), ["rate"]

        @staticmethod
        def rated_comment(value: int, queryset, user):
            return queryset.filter(rates__item_type="Comment", rates__item_id=value).annotate(
                rate=Sum("rates__rate", _filter=Q(rates__item_type="Comment", rates__item_id=value))
            ), ["rate"]

        @staticmethod
        def rated_event(value: int, queryset, user):
            return queryset.filter(rates__item_type="Event", rates__item_id=value).annotate(
                rate=Sum("rates__rate", _filter=Q(rates__item_type="Event", rates__item_id=value))
            ), ["rate"]
