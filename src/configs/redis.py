import os
import secrets

import redis.asyncio as redis
from fastapi import HTTPException


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

OTP_LENGTH = int(os.getenv("OTP_LENGTH", "6"))
OTP_EXPIRE_SECONDS = int(os.getenv("OTP_EXPIRE_SECONDS", "300"))  
VERIFIED_EXPIRE_SECONDS = int(os.getenv("VERIFIED_EXPIRE_SECONDS", "900"))  
MAX_OTP_ATTEMPTS = int(os.getenv("MAX_OTP_ATTEMPTS", "5"))


redis_client = redis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,  
)


async def close_redis() -> None:
    await redis_client.aclose()


def generate_otp(length: int = OTP_LENGTH) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))


async def create_email_otp(email: str) -> str:
    otp = generate_otp()

    await redis_client.set(f"email_otp:{email}", otp, ex=OTP_EXPIRE_SECONDS)
    await redis_client.delete(f"otp_attempts:{email}") 

    return otp


async def verify_email_otp(email: str, otp: str) -> bool:
    otp_key = f"email_otp:{email}"
    attempts_key = f"otp_attempts:{email}"

    attempts = await redis_client.incr(attempts_key)
    if attempts == 1:
        await redis_client.expire(attempts_key, OTP_EXPIRE_SECONDS)

    if attempts > MAX_OTP_ATTEMPTS:
        await redis_client.delete(otp_key)
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Please request a new OTP.",
        )

    stored_otp = await redis_client.get(otp_key)
    if stored_otp is None:
        raise HTTPException(status_code=400, detail="OTP expired or not found")

    if not secrets.compare_digest(stored_otp, otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    await redis_client.delete(otp_key, attempts_key)
    await redis_client.set(
        f"email_verified:{email}", "true", ex=VERIFIED_EXPIRE_SECONDS
    )

    return True


async def is_email_verified(email: str) -> bool:
    return await redis_client.get(f"email_verified:{email}") == "true"