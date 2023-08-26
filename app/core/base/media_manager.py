import boto3
import uuid
import re

from app.settings import config


class S3:
    client: None

    @staticmethod
    def init():
        S3.client = boto3.Session().client(
            's3',
            region_name=config.S3_REGION_NAME,
            endpoint_url=config.S3_END_POINT,
            aws_access_key_id=config.S3_SPACES_KEY,
            aws_secret_access_key=config.S3_SPACES_SECRET
        )

    @staticmethod
    def convert_cdn(url: str):
        return re.sub(r'(\w+)\.(\w+)\.digitaloceanspaces\.com', r'\1.\2.cdn.digitaloceanspaces.com', url)

    @staticmethod
    async def upload_file(file_type):
        filename = f"{uuid.uuid4()}.{file_type}"
        url = S3.client.generate_presigned_post(
            config.S3_BUCKET_NAME,
            f"{config.S3_BUCKET_NAME}/{filename}",
            ExpiresIn=3600,
            Conditions=[
                ["content-length-range", 100000, 1000000]  # allows 500kb
            ]
        )
        return url, filename

    @staticmethod
    async def get_file_url(filename: str):
        return S3.convert_cdn(
            S3.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': config.S3_BUCKET_NAME, 'Key': filename},
                ExpiresIn=3600  # 1 hour
            )
        )


S3.init()
