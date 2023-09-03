from typing import Optional

from app.core.base.filter_set import FilterSet
from .models import Hide, Report, Tag


class HideFilter(FilterSet):
    model = Hide

    class Parameters(FilterSet.Parameters):
        item_type: Optional[str] = None


class ReportFilter(FilterSet):
    model = Report
    search_fields = ["reason"]

    class Parameters(FilterSet.Parameters):
        item_type: Optional[Hide.ModelType] = None


class TagFilter(FilterSet):
    model = Tag
    search_fields = ["name"]

    class Parameters(FilterSet.Parameters):
        item_type: Optional[Tag.ModelType] = None
