"""Entry point for the Federation-Registry web app."""

import urllib.parse
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fed_reg.auth import configure_flaat
from fed_reg.config import API_V1_STR, API_V2_STR, get_settings
from fed_reg.db import set_neo4j_db_url
from fed_reg.logger import get_logger
from fed_reg.v1.router import router as router_v1
from fed_reg.v2.router import router as router_v2

settings = get_settings()

summary = "Federation-Registry (ex CMDB) REST API of the DataCloud project"
description = """
Federation-Registry (ex CMDB) stores providers data used by the DataCloud Orchestrator
to deploy new services.

You can inspect providers data, identity providers user groups and Service Level
Agreement connecting these data.

This database is mainly populated by scripts.
"""
version = "0.1.0"
contact = {
    "name": settings.MAINTAINER_NAME,
    "url": settings.MAINTAINER_URL,
    "email": settings.MAINTAINER_EMAIL,
}
tags_metadata = [
    {
        "name": API_V1_STR,
        "description": "API version 1, see link on the right",
        "externalDocs": {
            "description": "API version 1 documentation",
            "url": urllib.parse.urljoin(str(settings.BASE_URL), API_V1_STR + "docs"),
        },
    },
    {
        "name": API_V2_STR,
        "description": "API version 2, see link on the right",
        "externalDocs": {
            "description": "API version 2 documentation",
            "url": urllib.parse.urljoin(str(settings.BASE_URL), API_V2_STR + "docs"),
        },
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI application lifespan context manager.

    This function is called at application startup and shutdown. It performs:
    - Initializes the application logger and attaches it to the request state.
    - Configures authentication/authorization (Flaat).
    - Creates database tables if they do not exist.
    - Cleans up resources and disposes the database engine on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        dict: A dictionary with the logger instance, available in the request state.

    """
    logger = get_logger(settings)
    configure_flaat(settings, logger)
    set_neo4j_db_url(settings.DB_URL, logger)
    yield {"logger": logger}


app = FastAPI(
    contact=contact,
    description=description,
    openapi_tags=tags_metadata,
    summary=summary,
    title=settings.PROJECT_NAME,
    version=version,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sub_app_v1 = FastAPI(
    contact=contact,
    description=description,
    summary=summary,
    title=settings.PROJECT_NAME,
    version=version,
)
sub_app_v1.include_router(router_v1)
app.mount(API_V1_STR, sub_app_v1)

sub_app_v2 = FastAPI(
    contact=contact,
    description=description,
    summary=summary,
    title=settings.PROJECT_NAME,
    version=version,
)
sub_app_v2.include_router(router_v2)
app.mount(API_V2_STR, sub_app_v2)
