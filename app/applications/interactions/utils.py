from typing import Optional

from app.core.base.filter_set import FilterSet
from .models import Hide, Report


class HideFilter(FilterSet):
    model = Hide

    class Parameters(FilterSet.Parameters):
        item_type: Optional[str] = None


class ReportFilter(FilterSet):
    model = Report
    search_fields = ["reason"]

    class Parameters(FilterSet.Parameters):
        item_type: Optional[Hide.ModelType] = None
