from fastapi import APIRouter

from src.modules.auth.routes import auth_router

root_user_router = APIRouter(prefix="/auth")

root_user_router.include_router(auth_router, tags=["Admin Routes"])
