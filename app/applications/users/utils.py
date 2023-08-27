from tortoise.expressions import Subquery, Q
from datetime import datetime
from typing import Optional

from app.core.base.filter_set import FilterSet
from .models import User, Connection


async def update_last_login(user_id: int) -> None:
    user = await User.get(id=user_id)
    user.last_login = datetime.now()
    await user.save()


class UserFilter(FilterSet):
    model = User

    class Parameters(FilterSet.Parameters):
        posts: Optional[int] = None
        comments: Optional[int] = None
        hosted_events: Optional[int] = None
        attended_events: Optional[int] = None
        places: Optional[int] = None

    class SearchFields(FilterSet.SearchFields):
        username: str
        first_name: str
        last_name: str
        bio: str

    class FunctionFilters(FilterSet.FunctionFilters):
        connections: Optional[int] = None

    class Functions(FilterSet.Functions):
        @staticmethod
        def connections(value: int, queryset, user):
            return queryset.filter(
                Q(id__in=Subquery(Connection.filter(is_accepted=True, from_user_id=value).values('to_user_id'))) |
                Q(id__in=Subquery(Connection.filter(is_accepted=True, to_user_id=value).values('from_user_id')))
            )
