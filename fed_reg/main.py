"""Entry point for the Federation-Registry web app."""

import uvicorn
from fastapi import FastAPI

# from fastapi.middleware.cors import CORSMiddleware
from fed_reg.config import API_V1_STR, API_V2_STR, get_settings
from fed_reg.router import router_v1, router_v2

summary = "Federation-Registry (ex CMDB) of the DataCloud project"
description = """
Federation-Registry (ex CMDB) stores providers data used by the DataCloud Orchestrator
to deploy new services.

You can inspect providers data, identity providers user groups and Service Level
Agreement connecting these data.

This database is mainly populated by scripts.
"""
version = "0.1.0"

settings = get_settings()

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
            "url": f"{settings.DOC_V1_URL}",
        },
    },
    {
        "name": API_V2_STR,
        "description": "API version 2, see link on the right",
        "externalDocs": {
            "description": "API version 2 documentation",
            "url": f"{settings.DOC_V2_URL}",
        },
    },
]

app = FastAPI(
    contact=contact,
    description=description,
    openapi_tags=tags_metadata,
    summary=summary,
    title=settings.PROJECT_NAME,
    version=version,
    root_path=settings.ROOT_PATH,
)
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
