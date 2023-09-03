from fastapi import HTTPException, Query
from tortoise.queryset import QuerySet
from typing import Optional, Type
from enum import Enum

from app.applications.users.models import User
from .schemas import BaseOutSchema


class PageType(Enum):
    normal = "normal"
    random = "random"


class Paginator:
    def __init__(
        self,
        page: int = Query(1, ge=1, title="Page number"),
        page_size: int = Query(10, ge=1, le=100, title="Page size"),
        page_mode: PageType = Query(PageType.normal),
    ):
        self.page = page
        self.page_size = page_size
        self.page_mode = page_mode

    async def paginate(
        self,
        queryset: tuple[QuerySet, list],
        Serializer: Type[BaseOutSchema],
        current_user: Optional[User] = None,
    ) -> dict:
        if self.page < 1:
            raise HTTPException(status_code=400, detail="Invalid page number")
        annotations = queryset[1]
        queryset = queryset[0]

        total = await queryset.count()
        offset = (self.page - 1) * self.page_size

        page_data = [
            await Serializer.serialize(item=item, user=current_user, annotations=annotations)
            for item in await queryset.limit(self.page_size).offset(offset)
        ]

        return {
            "has_next": offset + self.page_size < total,
            "count": total,
            "results": page_data,
        }
