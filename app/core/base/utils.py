from fastapi import HTTPException

from .models import BaseDBModel


def get_object_or_404(Model, **kwargs):
    try:
        return Model.get(**kwargs)
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


def get_all_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


name2model = {cls.__name__: cls for cls in get_all_subclasses(BaseDBModel)}
