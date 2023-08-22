from fastapi import APIRouter, UploadFile, File, Depends
from botocore.client import Config
import boto3

from app.core.auth.utils.contrib import get_current_active_user
from app.settings import config

router = APIRouter()
s3_client = boto3.Session().client(
    's3',
    region_name=config.S3_REGION_NAME,
    endpoint_url=config.S3_END_POINT,
    aws_access_key_id=config.S3_SPACES_KEY,
    aws_secret_access_key=config.S3_SPACES_SECRET
)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user: str = Depends(get_current_active_user)):
    s3_client.upload_file(
        file.file,
        config.S3_BUCKET_NAME,
        file.filename,
        ExtraArgs={'ContentType': file.content_type}
    )
    return {"filename": file.filename, "status": "uploaded"}


@router.get("/{file_id}")
async def get_file_url(file_id: str):
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': config.S3_BUCKET_NAME, 'Key': file_id},
        ExpiresIn=3600,  # URL will expire in 1 hour
        Config=Config(signature_version='s3')
    )

    return {"url": url}
