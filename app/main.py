from tortoise.contrib.fastapi import register_tortoise
from firebase_admin import credentials, initialize_app
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import logging.config

from app.core.base.exceptions import APIException, on_api_exception
from app.settings import config

from app.applications.interactions.routes import notification_router
from app.applications.events.routes import router as events_router, category_router
from app.applications.users.routes import router as users_router
from app.core.auth.routes import router as auth_router
from app.core.fcm.routes import router as fcm_router
from app.applications.organisations.routes import router as organisations_router

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
app.include_router(auth_router, prefix='/api/auth')
app.include_router(users_router, prefix='/api/users')
app.include_router(events_router, prefix='/api/events')
app.include_router(category_router, prefix='/api/categories')
app.include_router(notification_router, prefix='/api/notifications')
app.include_router(fcm_router, prefix='/api/fcm')
app.include_router(organisations_router, prefix='/api/organisations')
