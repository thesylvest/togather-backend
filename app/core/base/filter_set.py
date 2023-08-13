from pydantic import BaseModel
from fastapi import Depends
from typing import Type


class FilterSet:
    model: Type

    class Parameters(BaseModel):
        pass

    @classmethod
    def apply_filters(cls, query_params: Parameters):
        filters = {field: value for field, value in query_params.dict().items() if value is not None}
        queryset = cls.model.filter(**filters)
        return queryset

    @classmethod
    def dependency(cls):
        def item_filter(query_params: cls.Parameters = Depends()):
            return cls.apply_filters(query_params)
        return item_filter
