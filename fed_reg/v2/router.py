"""Module with the V1 router architecture. Include all V1 endpoints."""

from fastapi import APIRouter

from fed_reg.v2.users.endpoints import user_router

router = APIRouter()
router.include_router(user_router)
