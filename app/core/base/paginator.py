from typing import Optional, Type, Any, Dict
from fastapi import HTTPException, Request
from tortoise.queryset import QuerySet
import re

from app.applications.users.models import User
from .schemas import BaseOutSchema


def increment(match):
    return "page=" + str(int(match.group(1)) + 1)


def decrement(match):
    return "page=" + str(int(match.group(1)) - 1)


async def paginate(
    queryset: QuerySet,
    page: int,
    page_size: int,
    request: Request,
    Serializer: Type[BaseOutSchema],
    request_user: Optional[User] = None,
) -> Dict[str, Any]:
    if page < 1:
        raise HTTPException(status_code=400, detail="Invalid page number")
    total = await queryset.count()
    offset = (page - 1) * page_size

    page_data = [
        await Serializer.serialize(item=item, user=request_user)
        for item in await queryset.limit(page_size).offset(offset)
    ]

    return {
        "links": {
            "next": re.sub(r"page=(\d+)", increment, str(request.url))
            if offset + page_size < total
            else None,
            "previous": re.sub(r"page=(\d+)", decrement, str(request.url))
            if page > 1
            else None,
        },
        "has_next": offset + page_size < total,
        "count": total,
        "results": page_data,
    }
