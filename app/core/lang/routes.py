from fastapi import APIRouter

from app.core.base.utils import get_object_or_404
from .models import Language, SupportedLanguages
from .schemas import LanguageSchema

router = APIRouter()


@router.get("/{lang}/", response_model=LanguageSchema, status_code=200, tags=['base'])
async def get_language(lang: SupportedLanguages):
    lang = await get_object_or_404(Language, lang=lang)
    return LanguageSchema(data=lang.data)
