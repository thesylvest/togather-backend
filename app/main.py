from tortoise.contrib.fastapi import register_tortoise
from firebase_admin import credentials, initialize_app
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import logging.config

from app.core.exceptions import APIException, on_api_exception
from app.settings import config

from app.applications.users.routers import router as users_router
from app.core.auth.routers import router as login_router
from app.core.fcm.routers import router as fcm_router

logging.config.dictConfig(config.DEFAULT_LOGGING)

app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    version=config.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)

app_list = [f'{config.APPLICATIONS_MODULE}.{app}.models' for app in config.APPLICATIONS]\
    + [f'{config.CORE_APPLICATIONS_MODULE}.{app}.models' for app in config.CORE_APPLICATIONS]
app_list.append('aerich.models')
tortoise_config = {
    'connections': {
        'default': config.DB_URL
    },
    'apps': {
        'models': {
            'models': app_list,
            'default_connection': 'default',
        }
    }
}

initialize_app(credentials.Certificate(config.FCM_CREDENTIALS))

register_tortoise(
    app,
    db_url=config.DB_URL,
    modules={'models': app_list},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.add_exception_handler(APIException, on_api_exception)
app.include_router(login_router, prefix='/api/auth/login')
app.include_router(users_router, prefix='/api/auth/users')
app.include_router(fcm_router, prefix='/api/fcm')
