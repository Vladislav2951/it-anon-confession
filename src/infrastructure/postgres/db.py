import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import get_settings


logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URI)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
