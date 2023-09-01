from tortoise.contrib.fastapi import register_tortoise
from firebase_admin import credentials, initialize_app
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from fastapi import FastAPI
import logging.config

from app.core.base.exceptions import APIException, on_api_exception
from app.settings import config


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

app.add_exception_handler(APIException, on_api_exception)

tortoise_config = {
    'connections': {
        'default': config.DB_URL
    },
    'apps': {
        'models': {
            'models': config.APP_LIST,
            'default_connection': 'default',
        }
    }
}

firebase_app = initialize_app(credentials.Certificate(config.FCM_CREDENTIALS))

register_tortoise(
    app,
    db_url=config.DB_URL,
    modules={'models': config.APP_LIST},
    generate_schemas=True,
    add_exception_handlers=True,
)

Tortoise.init_models(config.APP_LIST, "models")
# these imports must be after init models call
from app.applications.organisations.routes import club_router, place_router
from app.applications.posts.routes import post_router, comment_router
from app.applications.events.routes import router as events_router
from app.applications.users.routes import router as users_router
from app.applications.interactions.routes import interaction_router
from app.core.auth.routes import router as auth_router
from app.core.fcm.routes import router as fcm_router

app.include_router(auth_router, prefix='/api/auth')
app.include_router(users_router, prefix='/api/users')
app.include_router(events_router, prefix='/api/events')
app.include_router(club_router, prefix='/api/clubs')
app.include_router(place_router, prefix='/api/places')
app.include_router(post_router, prefix='/api/posts')
app.include_router(comment_router, prefix='/api/comments')
app.include_router(interaction_router, prefix='/api')
app.include_router(fcm_router, prefix='/api/fcm')


# TODO: add email support
# TODO: make foreign keys on delete logic
# TODO: login url with redirect capabilities
# TODO: change secret key with openssl rand -hex 32
# TODO: add pagination capabilities for regular, randomized, recommended etc.
# TODO: fetch user name and last name from email
# TODO: make search fields in a list of a Meta class or smth. like that
# TODO: apply ts vectors for search
# TODO: implement a manual cronjob
# TODO: check username if exists on google login
