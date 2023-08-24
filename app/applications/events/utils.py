from datetime import datetime
from typing import Optional

from app.core.base.filter_set import FilterSet, ListStr
from .models import Event


class EventFilter(FilterSet):
    class Parameters(FilterSet.Parameters):
        host_user__id__in: Optional[ListStr]
        host_club: Optional[int]
        host_user: Optional[int]
        attendees: Optional[int]
        category: Optional[int]
        start_date__gte: Optional[datetime]
        end_date__lte: Optional[datetime]
    model = Event
