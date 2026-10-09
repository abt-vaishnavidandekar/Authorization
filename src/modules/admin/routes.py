from fastapi import (
    APIRouter,
    Depends,
    Form,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.auth import get_current_user
from src.configs.database import get_db

from src.modules.admin.functions import register, get_admins, update_admin
from src.modules.admin.interface import (
    AdminCreate,
    AdminResponse,
)


admin_router = APIRouter(prefix="/admin", tags=["ADMIN Authentication"])


@admin_router.post("/register")
async def register_admin(data:AdminCreate, db:AsyncSession=Depends(get_db)):
    return await register(data=data, db=db)

@admin_router.get("/get_admin")
async def admins(db : AsyncSession=Depends(get_db)):
    return await get_admins(db=db)


@admin_router.put(
    "/admins/{admin_id}",
    response_model=AdminResponse
)
async def update_admin_details(
    admin_id: int,

    username: str | None = Form(default=None),
    email: str | None = Form(default=None),
    password: str | None = Form(default=None),

    current_user: dict = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(get_db)
):
    return await update_admin(
        db=db,
        admin_id=admin_id,
        current_user_id=current_user["user_id"],
        current_user_role=current_user["role"],
        username=username,
        email=email,
        password=password
    )

