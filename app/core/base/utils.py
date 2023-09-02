from fastapi import HTTPException


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
