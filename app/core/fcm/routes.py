from fastapi import APIRouter, Depends

from app.core.auth.utils.contrib import get_current_active_user
from .schemas import RegisterDeviceOut, RegisterDeviceIn
from app.applications.users.models import User
from .models import FCMDevice

router = APIRouter()


@router.post("/", response_model=RegisterDeviceOut, status_code=200, tags=['base'])
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
