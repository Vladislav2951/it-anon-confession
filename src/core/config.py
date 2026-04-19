from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from ipaddress import IPv4Address
from pathlib import Path
import tomllib
from typing import ClassVar, Literal, Union

from pydantic import IPvAnyAddress, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from libs.logger.custom_logger import LogLevel


_BASE_DIR = Path(__file__).parent.parent.parent


def _get_version_from_pyproject():
    try:
        return version("it-anon-confession")
    except PackageNotFoundError:
        pass

    try:
        pyproject_path = _BASE_DIR / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")
    except Exception:
        return "0.0.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: Literal["dev", "prod"] = "prod"
    VERSION: str = _get_version_from_pyproject()

    HOST: Union[IPvAnyAddress, Literal["localhost"]] = IPv4Address("0.0.0.0")
    PORT: int = 8000
    LOG_LEVEL: LogLevel = LogLevel.INFO

    SESSION_DURATION_DAYS: PositiveInt = 30

    CORS_ORIGINS: list[str] = []

    # postgres
    DB_ENGINE: str = "postgresql+asyncpg"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "postgres"
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: SecretStr = SecretStr("postgres")


@lru_cache
def get_settings():
    return Settings()


#         # date
#         self.DATETIME_FORMAT: str = "%d-%m-%Y T%H:%M:%S"
#         self.DATE_FORMAT: str = "%d-%m-%Y"
