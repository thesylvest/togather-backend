from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

from app.core.lang.models import SupportedLanguages
from .models import Admin


AdminOut = pydantic_model_creator(Admin)


class AdminCreate(BaseModel):
    username: str
    password: str


class LanguageCreate(BaseModel):
    lang: SupportedLanguages
    data: dict
