from typing import Optional

from app.core.base.filter_set import FilterSet, ListStr
from .models import Event


class EventFilter(FilterSet):
    class Parameters(FilterSet.Parameters):
        host_user__id__in: Optional[ListStr] = None
        host_user__id: Optional[str] = None
    model = Event
