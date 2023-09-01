from tortoise.contrib.pydantic.base import PydanticModel


class BaseOutSchema:
    pydantic_model = PydanticModel

    @classmethod
    async def serialize(cls, item, user, annotations=[]) -> dict:
        data = (await cls.pydantic_model.from_tortoise_orm(item)).dict()
        data.update(await cls.add_fields(item, user))
        for annotation in annotations:
            data[annotation] = getattr(item, annotation, None)
        return data

    @classmethod
    async def add_fields(cls, item, user) -> dict:
        return dict()
