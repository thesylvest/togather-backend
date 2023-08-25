from typing import Type, Optional, get_type_hints
from pydantic import BaseModel
from fastapi import Depends


class ListStr(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, handler):
        return {'type': 'str'}


class FilterSet:
    _type_hints_cache = {}
    model: Type

    class Parameters(BaseModel):
        pass

    @classmethod
    def apply_filters(cls, query_params: Parameters):
        filters = {
            field: cls.convert_actual_value(field, value)
            for field, value in query_params.dict().items() if value is not None
        }
        queryset = cls.model.filter(**filters)
        return queryset

    @classmethod
    def dependency(cls):
        def item_filter(query_params: cls.Parameters = Depends()):
            return cls.apply_filters(query_params)
        return item_filter

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
