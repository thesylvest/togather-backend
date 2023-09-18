from tortoise import models, fields
from enum import Enum

from app.core.base.media_manager import S3


class BaseDBModel(models.Model):
    class Meta:
        abstract = True
    id = fields.BigIntField(pk=True, index=True)


class BaseCreatedAtModel:
    created_at = fields.DatetimeField(auto_now_add=True)


class BaseCreatedUpdatedAtModel:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class LocationModel:
    latitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    location_decription = fields.CharField(max_length=512, null=True)


class MediaModel:
    media_dict = fields.JSONField(null=True)

    def media(self) -> list[str]:
        if self.media_dict:
            return [S3.get_file_url(media) if media != "" else "" for media in self.media_dict["media"]]
        return None


class ContentType:
    class ModelType(str, Enum):
        user = "User"
        post = "Post"
        comment = "Comment"
        event = "Event"
        club = "Club"
        place = "Place"
        hide = "Hide"
        report = "Report"
        attendee = "Attendee"
        tag = "Tag"
    item_type = fields.CharEnumField(enum_type=ModelType)
    item_id = fields.IntField()
