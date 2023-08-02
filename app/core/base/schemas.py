from pydantic import BaseModel

from app.applications.users.models import User


class ItemModel(BaseModel):
    class Config:
        from_attributes = True

    @staticmethod
    def allowed_actions(item, user: User | None) -> list[str]:
        return []  # item is a tortoise model and user is request user
