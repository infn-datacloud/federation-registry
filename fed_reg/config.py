"""Module with the configuration parameters."""

import logging
import os
from enum import Enum
from functools import lru_cache
from logging import Logger
from typing import Literal
from urllib.parse import urljoin

from neomodel import config
from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, EmailStr, Field, validator

API_V1_STR: str = "/api/v1"
API_V2_STR: str = "/api/v2"


class LogLevelEnum(int, Enum):
    """Enumeration of supported logging levels."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


def get_level(value: int | str | LogLevelEnum) -> int:
    """Convert a string, integer, or LogLevelEnum value to a logging level integer.

    Args:
        value: The log level as a string (case-insensitive), integer, or LogLevelEnum.

    Returns:
        int: The corresponding logging level integer.

    """
    if isinstance(value, str):
        return LogLevelEnum.__getitem__(value.upper())
    return value


def set_neo4j_db_url(neo4j_db_url: str, logger: Logger) -> AnyUrl:
    """
    Sets the Neo4j database URL in the configuration.

    Args:
        v (AnyUrl): The new database URL to set.

    Returns:
        AnyUrl: The same URL that was provided as input.
    """
    logger.info("Neo4j database URL: %s", neo4j_db_url)
    config.DATABASE_URL = neo4j_db_url


def build_doc_url(domain: AnyHttpUrl, root_path: str, api_version: str) -> str:
    """
    Builds a documentation URL based on the provided domain, root path, and API version.

    Args:
        domain (AnyHttpUrl): The domain to use in the URL.
        root_path (str): The root path to append to the domain. If not provided,
            defaults to an empty string.
        api_version (str): The API version to include in the URL path.

    Returns:
        str: The complete documentation URL as a string.
    """
    protocol = "http"
    root_path = root_path[1:] if root_path is not None else ""
    base_url = f"{protocol}://{domain!s}"
    path = os.path.join(root_path, api_version, "docs")
    return urljoin(base_url, path)


class Settings(BaseSettings):
    """Model with the app settings."""

    NEO4J_DB_URL: AnyUrl = Field(
        default="bolt://neo4j:password@localhost:7687",
        description="Neo4j complete connection URL. It contains the connection "
        "scheme, the user, the password, the server hostname and port.",
    )

    PROJECT_NAME: str = Field(
        default="Federation-Registry",
        description="Project name to display in the swagger documentation",
    )
    MAINTAINER_NAME: str | None = Field(
        default=None,
        description="Maintainer name to show in the swagger documentation",
    )
    MAINTAINER_URL: AnyHttpUrl | None = Field(
        default=None,
        description="Maintainer reference URL to show in the swagger documentation",
    )
    MAINTAINER_EMAIL: EmailStr = Field(
        default=None,
        description="Maintainer contact email to show in the swagger documentation",
    )
    DOMAIN: str = Field(
        default="localhost:8000",
        description="Base path to build the swagger documentation URL",
    )
    ROOT_PATH: str | None = Field(
        default=None, description="Root path to build the swagger documentation URL"
    )
    DOC_V1_URL: AnyHttpUrl | None = Field(
        default=None, description="URL to the V1 Documentation"
    )

    DOC_V2_URL: AnyHttpUrl | None = Field(
        default=None, description="URL to the V2 Documentation"
    )

    LOG_LEVEL: LogLevelEnum = Field(default=LogLevelEnum.INFO, description="Logs level")
    ADMIN_EMAIL_LIST: list[EmailStr] = Field(
        default_factory=list,
        description="List of the administrator's email. Used to authorize users. "
        "To be replaced by OPA",
    )
    TRUSTED_IDP_LIST: list[AnyHttpUrl] = Field(
        default_factory=list, description="List of trusted identity providers"
    )

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200",
    # "http://localhost:3000", "http://localhost:8080",
    # "http://local.dockertoolbox.tiangolo.com"]'
    # BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = ["http://localhost:3000"]
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl | Literal["*"]] = Field(
        default=["http://localhost:3000/"],
        description="JSON-formatted list of allowed origins",
    )

    @validator("LOG_LEVEL", pre=True)
    @classmethod
    def get_level(cls, value: int | str | LogLevelEnum) -> int:
        return get_level(value)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Retrieve cached settings."""
    return Settings()
