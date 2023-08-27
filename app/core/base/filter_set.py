from tortoise.expressions import Q, Subquery
from typing import Optional, get_type_hints
from tortoise.queryset import QuerySet
from pydantic import BaseModel
from fastapi import Depends
from tortoise import Model

from app.core.auth.utils.contrib import get_current_active_user_optional
from app.applications.interactions.models import Hide


class ListStr(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, handler):
        return {'type': 'str'}


class FilterSet:
    _type_hints_cache = {}
    _search_fields_cache = {}
    model: Model

    class Parameters(BaseModel):
        pass

    class SearchFields(BaseModel):
        pass

    class FunctionFilters(BaseModel):
        pass

    class Functions:
        pass

    @classmethod
    def apply_filters(cls, query_params: Parameters, queryset: QuerySet) -> QuerySet:
        filters = {
            field: cls.convert_actual_value(field, value)
            for field, value in query_params.dict().items() if value is not None
        }
        return queryset.filter(**filters)

    @classmethod
    def get_type_hint(cls, field_name: str):
        if cls not in cls._type_hints_cache:
            cls._type_hints_cache[cls] = get_type_hints(cls.Parameters)
        return cls._type_hints_cache[cls][field_name]

    @classmethod
    def convert_actual_value(cls, field_name: str, value_str: str):
        if cls.get_type_hint(field_name) == Optional[ListStr]:
            return value_str.split(",")
        return value_str

    @classmethod
    def search(cls, search_text: str, queryset: QuerySet) -> QuerySet:
        if search_text is None:
            return queryset
        search_queries = (
            Q(**{f"{field}__icontains": search_text})
            for field in cls.get_search_fields()
        )
        return queryset.filter(Q(*search_queries, join_type="OR"))

    @classmethod
    def get_search_fields(cls):
        if cls not in cls._search_fields_cache:
            cls._search_fields_cache[cls] = list(cls.SearchFields.schema()["properties"].keys())
        return cls._search_fields_cache[cls]

    @classmethod
    def apply_function_filters(cls, function_filters: FunctionFilters, queryset, user):
        for method, value in function_filters.dict().items():
            if value is None:
                continue
            queryset = getattr(cls.Functions, method)(value, queryset, user)
        return queryset

    @classmethod
    def dependency(cls):
        def item_filter(
                search_text: str = None,
                get_blocked: str = None,
                query_params: cls.Parameters = Depends(),
                function_filters: cls.FunctionFilters = Depends(),
                current_user=Depends(get_current_active_user_optional)
        ):
            if not current_user:
                queryset = cls.model.all()
            else:
                hide_filter = Q(id__in=Subquery(Hide.filter(hider=current_user, item_type=cls.model.__name__).values("item_id")))
                if get_blocked is None:  # TODO: add blocked user filter too
                    queryset = cls.model.filter(~hide_filter)
                else:
                    queryset = cls.model.filter(hide_filter)
            filtered_query = cls.apply_filters(query_params, queryset)
            searched_query = cls.search(search_text, filtered_query)
            function_query = cls.apply_function_filters(function_filters, searched_query, current_user)
            print(function_query.sql())
            return function_query
        return item_filter
