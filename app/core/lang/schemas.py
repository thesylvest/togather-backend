from pydantic import BaseModel


class LanguageSchema(BaseModel):
    data: dict
