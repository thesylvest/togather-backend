from fastapi import APIRouter, Depends, Query, Request

from app.core.auth.utils.contrib import get_current_active_user, get_current_active_superuser
from .schemas import RegisterDeviceOut, RegisterDeviceIn, DeviceOut
from app.applications.users.models import User
from app.core.fcm.utils import FCMDeviceFilter
from app.core.base.paginator import paginate
from .models import FCMDevice

router = APIRouter()


@router.post("/", response_model=RegisterDeviceOut, status_code=200, tags=['devices'])
async def get_or_register_device(
    device_in: RegisterDeviceIn,
    current_user: User = Depends(get_current_active_user),
):
    """
    Gets device if it already exists otherwise it creates this device
    """
    device, created = await FCMDevice.get_or_create(
        name=device_in.name,
        user=current_user,
        device_id=device_in.device_id,
        registration_id=device_in.registration_id,
        device_type=device_in.device_type
    )
    return RegisterDeviceOut(device=device.device_id, created=created)


@router.get("/", status_code=200, tags=['devices'])
async def device(
    request: Request,
    page: int = Query(1, ge=1, title="Page number"),
    page_size: int = Query(10, ge=1, le=100, title="Page size"),
    current_user: User = Depends(get_current_active_user),  # TODO: make superuser
    devices=Depends(FCMDeviceFilter.dependency()),
):
    """
    Gets device list
    """
    return await paginate(devices, page, page_size, request, DeviceOut, current_user)
