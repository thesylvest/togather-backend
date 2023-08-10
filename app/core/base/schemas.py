from pydantic import BaseModel


class BaseOutSchema(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    @classmethod
    def serialize(cls, item, user) -> dict:
        """
        The item is a orm model, and user can be none or request.user
        """
        data: dict = cls.from_orm(item).dict()
        data.update(cls.add_fields(item, user))
        return data

    @classmethod
    def add_fields(cls, item, user) -> dict:
        """
        The item is a orm model, and user can be none or request.user
        """
        raise NotImplementedError
    

class BaseInSchema(BaseModel):
    def to_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude_none=True,
            exclude={"id"},
        )
