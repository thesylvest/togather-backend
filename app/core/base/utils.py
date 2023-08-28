from typing import List, Type, Tuple
from fastapi import HTTPException
from pydantic import BaseModel

from app.core.base.media_manager import S3


async def get_object_or_404(Model, **kwargs):
    try:
        return await Model.get(**kwargs)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Object not found!"
        )


async def has_permission(method, user):
    if not await method(user):
        raise HTTPException(
            status_code=403,
            detail="Insufficient privilege"
        )


def extract_mentions_and_tags(Model: Type[BaseModel], fields: List[str]):
    def _extract_mentions_and_tags(data: Model) -> Tuple[List[str], List[str]]:
        usernames = []
        hashtags = []
        for field in fields:
            text = getattr(data, field, "")
            usernames += [word[1:] for word in text.split() if word.startswith("@")]
            hashtags += [word[1:] for word in text.split() if word.startswith("#")]
        return usernames, hashtags
    return _extract_mentions_and_tags


async def extract_media_files(data: BaseModel, item=None) -> Tuple[List[dict], List[str]]:
    data = data.dict(exclude_none=True, exclude=["media"])
    urls = []
    media = []
    if data.media:
        for media_dict in data.media:
            if item and media_dict.get("name", None) not in item.media["media"]:
                url, name = S3.upload_file(media_dict["file_type"])
                urls.append(url)
            else:
                name = media_dict["name"]
            media.append(name)
        data["media"] = {"media": media}
    return urls, data
