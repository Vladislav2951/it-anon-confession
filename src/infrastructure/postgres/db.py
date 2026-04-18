from logging import getLogger

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import get_settings


logger = getLogger(__name__)

settings = get_settings()

DATABASE_URI = "{db_engine}://{username}:{password}@{host}:{port}/{database}".format(
    db_engine=settings.DB_ENGINE,
    username=settings.DB_USERNAME,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

engine = create_async_engine(DATABASE_URI)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# async def get_async_session():
#     async with async_session_maker() as session:
#         yield session
