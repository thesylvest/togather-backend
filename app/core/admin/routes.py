from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from tortoise.exceptions import IntegrityError

from app.applications.organisations.models import Place, Club
from .schemas import AdminCreate, LanguageCreate, AdminOut
from app.applications.interactions.models import Category
from .utils import get_password_hash, get_current_admin
from app.core.base.utils import get_object_or_404
from app.core.base.media_manager import S3
from app.core.lang.models import Language
from .models import Admin

router = APIRouter()


@router.post("/init/", tags=["admin"])
async def init_admin(admin: AdminCreate):
    count = await Admin.all().count()
    if count == 0:
        hashed_password = get_password_hash(admin.password)
        try:
            await Admin.create(username=admin.username, password=hashed_password)
            return {"status": "Admin created"}
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Admin already exists")
    else:
        raise HTTPException(status_code=400, detail="Admin already exists")


@router.get("/", tags=["admin"])
async def get_admins(
    current_admin: Admin = Depends(get_current_admin),
):
    return await AdminOut.from_queryset(Admin.all())


@router.post("/", tags=["admin"])
async def create_admin(
    admin: AdminCreate,
    current_admin: Admin = Depends(get_current_admin),
):
    hashed_password = get_password_hash(admin.password)
    try:
        await Admin.create(username=admin.username, password=hashed_password)
        return {"status": "Admin created"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Admin already exists")


@router.delete("/{id}/", tags=["admin"])
async def delete_admin(
    id: int,
    current_admin: Admin = Depends(get_current_admin),
):
    admin: Admin = await get_object_or_404(Admin, id=id)
    await admin.delete()


@router.post("/places/{id}/", tags=["admin"])
async def verify_place(
    id: int,
    current_admin: Admin = Depends(get_current_admin),
):
    place: Place = await get_object_or_404(Place, id=id)
    place.is_verified = not place.is_verified
    await place.save()

    return {"message": f"New status of place {id} is {place.is_verified}"}


@router.post("/clubs/{id}/", tags=["admin"])
async def verify_club(
    id: int,
    current_admin: Admin = Depends(get_current_admin),
):
    club: Club = await get_object_or_404(Club, id=id)
    club.is_verified = not club.is_verified
    await club.save()

    return {"message": f"New status of club {id} is {club.is_verified}"}


@router.post("/categories/{name}", status_code=201, tags=['admin'])
async def create_or_update_category(
    name: str,
    category_picture: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin),
):
    category, _ = await Category.get_or_create(name=name)
    extension = category_picture.filename.split(".")[1]
    url, filename = S3.upload_file(extension)
    category.picture_name = filename
    await category.save()
    cdn_response = S3.upload_file_to_space(url, category_picture.file)
    return {"message": "category created or updated", "category": category, "cdn status code": cdn_response.status_code}


@router.delete("/categories/{name}", status_code=201, tags=['admin'])
async def delete_category(
    name: str,
    current_admin: Admin = Depends(get_current_admin),
):
    category: Category = await get_object_or_404(Category, name=name)
    await category.delete()
    return {"message": "category deleted"}


@router.post("/languages/", status_code=201, tags=['admin'])
async def create_or_update_language(
    lang_in: LanguageCreate,
    current_admin: Admin = Depends(get_current_admin),
):
    lang, created = await Language.get_or_create(lang=lang_in.lang)
    await lang.update_from_dict({"data": lang_in.data}).save()
    return {"message": "language created"}


@router.delete("/languages/{lang}", status_code=201, tags=['admin'])
async def delete_languages(
    lang: str,
    current_admin: Admin = Depends(get_current_admin),
):
    language: Language = await get_object_or_404(Language, lang=lang)
    await language.delete()
    return {"message": "language deleted"}
