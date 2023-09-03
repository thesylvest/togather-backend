from fastapi import APIRouter, Depends

from app.core.auth.utils.contrib import get_current_active_superuser
from app.core.base.utils import get_object_or_404
from .models import Language, SupportedLanguages
from .schemas import LanguageSchema

router = APIRouter()


@router.post("/{lang}", response_model=LanguageSchema, status_code=201, tags=['base'])
async def create_language(
    lang: SupportedLanguages,
    lang_in: LanguageSchema,
    current_user=Depends(get_current_active_superuser),
):
    lang, created = await Language.get_or_create(lang=lang)
    await lang.update_from_dict({"data": lang_in.data}).save()
    return LanguageSchema(data=lang.data)


@router.get("/{lang}", response_model=LanguageSchema, status_code=200, tags=['base'])
async def get_language(lang: SupportedLanguages):
    lang = await get_object_or_404(Language, lang=lang)
    return LanguageSchema(data=lang.data)
