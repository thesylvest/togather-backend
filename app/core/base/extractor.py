from pydantic import BaseModel

from app.core.base.media_manager import S3


class Extractor:
    def __init__(self, data: BaseModel):
        self.data = data

    def tags(self, fields):
        hashtags = []
        for field in fields:
            text = getattr(self.data, field, "")
            hashtags += [word[1:] for word in text.split() if word.startswith("#")]
        return hashtags

    def mentions(self, fields):
        usernames = []
        for field in fields:
            text = getattr(self.data, field, "")
            usernames += [word[1:] for word in text.split() if word.startswith("@")]
        return usernames

    def media_files(self, item=None):
        urls = []
        media = []
        if self.data.media:
            for media_dict in self.data.media:
                if media_dict.get("empty", False):
                    name = ""
                elif item and item.media_dict and media_dict.get("name", None) not in item.media_dict["media"]:
                    url, name = S3.upload_file(media_dict["file_type"])
                    urls.append(url)
                elif (item is None) or (item.media_dict is None):
                    url, name = S3.upload_file(media_dict["file_type"])
                    urls.append(url)
                else:
                    name = media_dict["name"]
                media.append(name)
        return urls, {"media": media}
