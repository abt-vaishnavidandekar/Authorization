from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from configs.security import verify_password, create_access_token, create_refresh_token
from src.modules.admin.models import Admin
from src.modules.users.models import User
from jose import jwt, JWTError
from configs.security import ALGORITHM, SECRET_KEY
from fastapi.responses import JSONResponse
from fastapi import status
import secrets
from configs.redis import redis_client, OTP_EXPIRE_SECONDS, MAX_OTP_ATTEMPTS, VERIFIED_EXPIRE_SECONDS

async def login_user(db: AsyncSession, email: str, password: str):

    result = await db.execute(select(Admin).where(Admin.email == email))
    admin = result.scalar_one_or_none()

    if admin:
        if not verify_password(password, admin.password):
            return None
        return {
            "access_token": create_access_token(user_id=admin.id, role="admin"),
            "refresh_token": create_refresh_token(user_id=admin.id, role="admin"),
        }

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        if not verify_password(password, user.password):
            return None
        return {
            "access_token": create_access_token(user_id=user.id, role="user"),
            "refresh_token": create_refresh_token(user_id=user.id, role="user"),
        }

    return None


def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        role = payload.get("role")
        token_type = payload.get("type")

        if not user_id or not role or token_type != "refresh":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content = {
                    "success" : False,
                    "msg" : "Invalid Refresh token"
                }
            )

        return create_access_token(user_id=int(user_id), role=role)

    except JWTError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content = {
                "success" : False,
                "msg" : "Access token expired"
            }
        )


def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


async def create_email_otp(email: str) -> str:
    otp = generate_otp()

    await redis_client.set(f"email_otp:{email}", otp, ex=OTP_EXPIRE_SECONDS)
    await redis_client.delete(f"otp_attempts:{email}")  

    return otp


async def verify_email_otp(email: str, otp: str) -> bool:
    otp_key = f"email_otp:{email}"
    attempts_key = f"otp_attempts:{email}"

    attempts = await redis_client.get(attempts_key)
    if attempts is not None and int(attempts) >= MAX_OTP_ATTEMPTS:
        await redis_client.delete(otp_key)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            context={
                "success" : False,
                "msg" : "Too many attempts"
            }
        )

    stored_otp = await redis_client.get(otp_key)

    if stored_otp is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            context={
                "success" : False,
                "msg" : "OTP expire or not found"
            }
        )

    if isinstance(stored_otp, bytes):
        stored_otp = stored_otp.decode()

    if not secrets.compare_digest(stored_otp, otp):
        await redis_client.incr(attempts_key)
        await redis_client.expire(attempts_key, OTP_EXPIRE_SECONDS)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            context={
                "success" : False,
                "msg" : "Invalid OTP"
            }
        )

    await redis_client.delete(otp_key)
    await redis_client.delete(attempts_key)
    await redis_client.set(
        f"email_verified:{email}", "true", ex=VERIFIED_EXPIRE_SECONDS
    )

    return True

