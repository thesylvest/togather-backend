from tortoise.contrib.pydantic.base import PydanticModel


class BaseOutSerializer:
    @classmethod
    async def serialize(cls, item, user) -> dict:
        """
        The item is a orm model, and user can be none or request.user
        """
        raise NotImplementedError

    @classmethod
    async def add_fields(cls, item, user) -> dict:
        """
        The item is a orm model, and user can be none or request.user
        """
        return dict()


class BaseOutSchema(BaseOutSerializer):
    pydantic_model = PydanticModel

    @classmethod
    async def serialize(cls, item, user) -> dict:
        data = (await cls.pydantic_model.from_tortoise_orm(item)).dict()
        data.update(await cls.add_fields(item, user))
        return data
