from .interface import LoginRequest, RefreshRequest, SendOtpRequest, VerifyOtpRequest
from fastapi import APIRouter, Depends, status
from configs.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from .functions import refresh_access_token, create_refresh_token, login_user, create_email_otp, verify_email_otp, OTP_EXPIRE_SECONDS

auth_router = APIRouter(prefix="/admin", tags=["ADMIN Authentication"])

@auth_router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    tokens = await login_user(db, data.email, data.password)

    if not tokens:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            context = {
                "success" : False,
                "msg" : "Invalid credentials"
            }
        )

    return tokens


@auth_router.post("/refresh")
def refresh(data: RefreshRequest):
    return {"access_token": refresh_access_token(data.refresh_token)}


@auth_router.post("/send-otp")
async def send_otp(data: SendOtpRequest):
    otp = await create_email_otp(data.email)

    return {
        "message": "OTP generated successfully",
        "otp": otp, 
        "expires_in": OTP_EXPIRE_SECONDS,
    }


@auth_router.post("/verify-otp")
async def verify_otp(data: VerifyOtpRequest):
    await verify_email_otp(data.email, data.otp)

    return {"message": "Email verified successfully"}