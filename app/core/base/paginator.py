from fastapi import HTTPException, Request, Query
from tortoise.queryset import QuerySet
from typing import Optional, Type

from app.applications.users.models import User
from .schemas import BaseOutSchema


class Paginator:
    def __init__(
        self,
        page: int = Query(1, ge=1, title="Page number"),
        page_size: int = Query(10, ge=1, le=100, title="Page size"),
        request: Request = None,
    ):
        self.page = page
        self.page_size = page_size
        self.request = request

    async def paginate(
        self,
        queryset: QuerySet,
        Serializer: Type[BaseOutSchema],
        current_user: Optional[User] = None
    ) -> dict:
        if self.page < 1:
            raise HTTPException(status_code=400, detail="Invalid page number")
        total = await queryset.count()
        offset = (self.page - 1) * self.page_size

        page_data = [
            await Serializer.serialize(item=item, user=current_user)
            for item in await queryset.limit(self.page_size).offset(offset)
        ]

        return {
            "has_next": offset + self.page_size < total,
            "count": total,
            "results": page_data,
        }
