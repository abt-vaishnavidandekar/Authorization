

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.admin.models import Admin
from src.configs.security import hash_password
from .interface import AdminCreate, AdminResponse
from fastapi.responses import JSONResponse
from fastapi import status

async def register(data: AdminCreate, db : AsyncSession):
    result = await db.execute(select(Admin).where(Admin.email == data.email))
    admin = result.scalar_one_or_none()

    if admin:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success" : False,
                "msg" : "Email already exists"
            }
        )

    if len(data.password) < 8:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success" : False,
                "msg" : "Password length should be minimum 8"
            }
    )

    hashed_password = hash_password(data.password)

    admin = Admin(
    username=data.username,
    email=data.email,
    password=hashed_password
    )

    db.add(admin)

    await db.commit()

    await db.refresh(admin)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success" : True,
            "msg" : "Admin data Saved Successfully"
        }     
    )


async def get_admins(db: AsyncSession):
    result = await db.execute(select(Admin))

    admin = result.scalars().all()

    return admin


async def update_admin(
    db: AsyncSession,
    admin_id: int,
    current_user_id: int,
    current_user_role: str,
    username: str | None = None,
    email: str | None = None,
    password: str | None = None
):


    if current_user_role != "admin":
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            context = {
                "success" : False,
                "msg" : "Only admin can update details"
            }
        )

    if admin_id != current_user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            context = {
                "success" : False,
                "msg" : "You can only update your own details"
            }
        )
    result = await db.execute(
        select(Admin).where(
            Admin.id == admin_id
        )
    )

    admin = result.scalar_one_or_none()

    if not admin:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            context = {
                "success" : False,
                "msg" : "Admin Not found"
            }
        )

    if username is not None:

        username_result = await db.execute(
            select(Admin).where(
                Admin.username == username,
                Admin.id != admin_id
            )
        )

        existing_username = (
            username_result.scalar_one_or_none()
        )

        if existing_username:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                context = {
                    "success" : False,
                    "msg" : "User already Exists"
                }
            )

        admin.username = username

    if email is not None:

        email_result = await db.execute(
            select(Admin).where(
                Admin.email == email,
                Admin.id != admin_id
            )
        )

        existing_email = (
            email_result.scalar_one_or_none()
        )

        if existing_email:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                context = {
                    "success" : False,
                    "msg" : "Email already exists"
                }
            )

        admin.email = email

    if password is not None:
        admin.password = hash_password(
            password
        )

    await db.commit()

    await db.refresh(admin)

    return admin