from fastapi import APIRouter

from src.modules.admin.routes import admin_router

root_user_router = APIRouter(prefix="/user")

root_user_router.include_router(admin_router, tags=["Admin Routes"])
