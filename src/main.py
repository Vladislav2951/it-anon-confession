from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from api.http.routes import routers
from core.config import get_settings
from libs.logger.custom_logger import setup_logging


settings = get_settings()

logger = setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO check db connection

    yield


app = FastAPI(title="it-anon-confession", version=settings.VERSION, lifespan=lifespan)


if settings.CORS_ORIGINS:
    logger.debug("CORS Origins: %s", settings.CORS_ORIGINS)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Добавляем middleware
# app.add_middleware(AuthMiddleware) # type: ignore[attr-defined]

# Переопределение обработчика HTTP ошибок
# app.add_exception_handler(HTTPException, http_exception_handler)


@app.get("/")
def root():
    return {"message": "OK"}


app.include_router(routers)
