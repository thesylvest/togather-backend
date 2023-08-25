import os

VERSION = '0.0.0'
APP_TITLE = 'ToGather Backend'
PROJECT_NAME = 'Backend Server'
APP_DESCRIPTION = 'ToGather Backend'

SERVER_HOST = 'localhost'

DEBUG = "T"

APPLICATIONS_MODULE = 'app.applications'
CORE_APPLICATIONS_MODULE = 'app.core'
APPLICATIONS = [
    'users',
    'events',
    'posts',
    'interactions',
    'organisations',
]
CORE_APPLICATIONS = [
    'fcm'
]

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
BASE_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
LOGS_ROOT = os.path.join(BASE_DIR, "app/logs")
EMAIL_TEMPLATES_DIR = os.path.join(BASE_DIR, "app/templates/")

S3_REGION_NAME = os.getenv("S3_REGION_NAME", "fra1")
S3_END_POINT = os.getenv("S3_END_POINT", 'https://togather-space.fra1.digitaloceanspaces.com')
S3_SPACES_KEY = os.getenv("S3_SPACES_KEY", 'XXXXXXXXXXXXXXXXXXXX')
S3_SPACES_SECRET = os.getenv("S3_SPACES_SECRET", 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
S3_BUCKET_NAME = "media"

DB_URL = os.getenv('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/main')

# TODO: change secret key with $(openssl rand -hex 32)
SECRET_KEY = '3488a63e1765035d386f05409663f55c83bfae3b3c61a932744b20ad14244dcf' if DEBUG == "T" else os.getenv('SECRET_KEY')
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 day

EMAILS_FROM_NAME = ''
EMAILS_FROM_EMAIL = ''
SMTP_USER = ''
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_TLS = True
SMTP_PASSWORD = ''
EMAIL_RESET_TOKEN_EXPIRE_HOURS = 1
EMAILS_ENABLED = SMTP_HOST and SMTP_PORT and EMAILS_FROM_EMAIL

FCM_CREDENTIALS = os.path.join(BASE_DIR, "credentials.json")

LOGIN_URL = SERVER_HOST + '/api/auth/login/access-token'

CORS_ORIGINS = [
    "http://localhost"
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
