import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.http.routes import routers
from core.config import get_settings
from libs.logger.custom_logger import setup_logging


settings = get_settings()

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


app = FastAPI(title="it-anon-confession", version=settings.VERSION)


if settings.CORS_ORIGINS:
    logger.debug("CORS Origins: %s", settings.CORS_ORIGINS)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
def root():
    return {"message": "OK"}


app.include_router(routers)
