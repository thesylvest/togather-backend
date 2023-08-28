from typing import Optional

from app.core.base.filter_set import FilterSet
from .models import Hide, Report


class HideFilter(FilterSet):
    model = Hide

    class Parameters(FilterSet.Parameters):
        item_type: Optional[str] = None


class ReportFilter(FilterSet):
    model = Report

    class Parameters(FilterSet.Parameters):
        item_type: Optional[str] = None

    class SearchFields(FilterSet.SearchFields):
        reason: str
