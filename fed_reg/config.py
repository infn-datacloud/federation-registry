"""Module with the configuration parameters."""

import os
from enum import Enum
from functools import lru_cache
from typing import Any, Optional

from neomodel import config
from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, EmailStr, Field, validator


class Neo4jUriScheme(str, Enum):
    """Enumeration with the accepted neo4j schemas."""

    NEO4J: str = "neo4j"
    NEO4JS: str = "neo4j+s"
    BOLT: str = "bolt"
    BOLTS: str = "bolt+s"


class Settings(BaseSettings):
    """Model with the app settings."""

    PROJECT_NAME: str = "Federation-Registry"
    DOMAIN: str = "localhost:8000"
    API_V1_STR: str = "/api/v1"
    ROOT_PATH: str | None = None

    @validator("API_V1_STR")
    @classmethod
    def start_with_single_slash(cls, v: str) -> str:
        """String must start with a single slash."""
        assert v.startswith("/"), ValueError("API V1 string must start with '/'")
        assert len(v) > 1, ValueError(
            "API V1 string can't have an empty string after the '/'"
        )
        return v

    NEO4J_SERVER: str = "localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    NEO4J_URI_SCHEME: Neo4jUriScheme = Field(default=Neo4jUriScheme.BOLT)
    NEO4J_DB_URL: Optional[AnyUrl] = None

    @validator("NEO4J_URI_SCHEME")
    @classmethod
    def get_enum_val(cls, v: Neo4jUriScheme) -> str:
        """Retrive the string from the enum value."""
        return v.value

    @validator("NEO4J_DB_URL", pre=True)
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> str:
        """Before checking the DB URL, assemble the target DB uri from single parts."""
        if v:
            return v
        s = f"{values.get('NEO4J_URI_SCHEME')}://"
        s += f"{values.get('NEO4J_USER')}:"
        s += f"{values.get('NEO4J_PASSWORD')}@"
        s += f"{values.get('NEO4J_SERVER')}"
        return s

    @validator("NEO4J_DB_URL")
    @classmethod
    def set_neo4j_db_url(cls, v: AnyUrl) -> AnyUrl:
        """Set the DATABASE_URL."""
        config.DATABASE_URL = str(v)
        return v

    MAINTAINER_NAME: Optional[str] = None
    MAINTAINER_URL: Optional[AnyHttpUrl] = None
    MAINTAINER_EMAIL: Optional[EmailStr] = None

    ADMIN_EMAIL_LIST: list[EmailStr] = []
    TRUSTED_IDP_LIST: list[AnyHttpUrl] = []

    DOC_V1_URL: Optional[AnyHttpUrl] = None

    @validator("DOC_V1_URL", pre=True)
    @classmethod
    def create_doc_url(cls, v: Optional[str], values: dict[str, Any]) -> str:
        """Build URL for internal documentation."""
        if v:
            return v
        protocol = "http"
        root_path = values.get("ROOT_PATH", "/")
        root_path = root_path[1:] if root_path is not None else ""
        link = os.path.join(
            values.get("DOMAIN"), root_path, values.get("API_V1_STR")[1:], "docs"
        )
        return f"{protocol}://{link}"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200",
    # "http://localhost:3000", "http://localhost:8080",
    # "http://local.dockertoolbox.tiangolo.com"]'
    # BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = ["http://localhost:3000"]

    class Config:
        """Sub class to set attribute as case sensitive."""

        case_sensitive = True
        validate_assignment = True


@lru_cache
def get_settings() -> Settings:
    """Retrieve cached settings."""
    return Settings()
