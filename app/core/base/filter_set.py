from tortoise.expressions import Q, Subquery
from tortoise.queryset import QuerySet
from fastapi import Depends, Query
from pydantic import BaseModel
from typing import Optional
from tortoise import Model
from enum import Enum

from app.core.auth.utils.contrib import get_current_active_user_optional


class FilterMode(Enum):
    regular = "regular"
    hidden = "hidden"
    blocked = "blocked"
    all = "all"


class FilterSet:
    model: Model
    search_fields: list[str]

    @classmethod
    def hide(cls, user):
        return Q(id__in=Subquery(user.hides.filter(item_type=cls.model.__name__).values("item_id")))

    @classmethod
    def block(cls, user):
        return Q()

    class Parameters(BaseModel):
        pass

    class FunctionFilters(BaseModel):
        pass

    class Functions:
        pass

    @classmethod
    def apply_filters(cls, query_params: Parameters, queryset: QuerySet) -> QuerySet:
        return queryset.filter(**{k: v for k, v in query_params.dict().items() if v is not None})

    @classmethod
    def search(cls, search_text: str, queryset: QuerySet) -> QuerySet:
        if search_text is None:
            return queryset
        search_queries = (Q(**{f"{field}__icontains": search_text}) for field in cls.search_fields)
        return queryset.filter(Q(*search_queries, join_type="OR"))

    @classmethod
    def apply_function_filters(cls, function_filters: FunctionFilters, queryset, user):
        annotations: list[str] = []
        for method, value in function_filters.dict().items():
            if value is not None:
                queryset, annotate = getattr(cls.Functions, method)(value, queryset, user)
                annotations = annotations + annotate
        return queryset, annotations

    @classmethod
    def dependency(cls):
        def item_filter(
                filter_mode: FilterMode = Query(FilterMode.regular),
                search_text: Optional[str] = None,
                query_params: cls.Parameters = Depends(),
                function_filters: cls.FunctionFilters = Depends(),
                current_user=Depends(get_current_active_user_optional)
        ):
            if not current_user:
                queryset = cls.model.all()
            else:
                if filter_mode == FilterMode.all:
                    queryset = cls.model.all()
                elif filter_mode == FilterMode.regular:
                    queryset = cls.model.exclude(cls.hide(current_user) | cls.block(current_user))
                elif filter_mode == FilterMode.hidden:
                    queryset = cls.model.filter(cls.hide(current_user))
                elif filter_mode == FilterMode.blocked:
                    queryset = cls.model.filter(cls.block(current_user))
            filtered_query = cls.apply_filters(query_params, queryset)
            searched_query = cls.search(search_text, filtered_query)
            function_query, annotations = cls.apply_function_filters(function_filters, searched_query, current_user)
            print("======================================")
            print(annotations)
            print(function_query.sql())
            print("======================================")
            return function_query, annotations
        return item_filter
