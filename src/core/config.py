from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from ipaddress import IPv4Address
from pathlib import Path
import tomllib
from typing import Literal, Union

from pydantic import IPvAnyAddress, PositiveInt
from pydantic_settings import BaseSettings

from libs.logger.custom_logger import LogLevel


BASE_DIR = Path(__file__).parent.parent.parent


def _get_version_from_pyproject():
    try:
        return version("it-anon-confession")
    except PackageNotFoundError:
        pass

    try:
        pyproject_path = BASE_DIR / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")
    except Exception:
        return "0.0.0"


class Settings(BaseSettings):
    ENV: Literal["dev", "prod"] = "prod"

    HOST: Union[IPvAnyAddress, Literal["localhost"]] = IPv4Address("0.0.0.0")
    PORT: int = 8000
    LOG_LEVEL: LogLevel = LogLevel.INFO

    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: PositiveInt = 15

    VERSION: str = _get_version_from_pyproject()

    CORS_ORIGINS: list[str] = []

    # BASE_URL: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


#         # date
#         self.DATETIME_FORMAT: str = "%d-%m-%Y T%H:%M:%S"
#         self.DATE_FORMAT: str = "%d-%m-%Y"

#         # auth
#         self.SESSION_DURATION_DAYS: int = int(os.getenv("SESSION_DURATION_DAYS", 7))


#         # postgres
#         self.DB_ENGINE: str = "postgresql+asyncpg"
#         self.DB_HOST: str = os.getenv("DB_HOST", "localhost")
#         self.DB_PORT: str = os.getenv("DB_PORT", "3306")
#         self.DB_NAME: str = os.getenv("DB_NAME", "postgres")  # TODO raise error when None
#         self.DB_USERNAME: str = os.getenv("DB_USERNAME", "postgres")
#         self.DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
