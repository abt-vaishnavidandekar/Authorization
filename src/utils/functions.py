from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from src.configs.security import create_email_otp, verify_email_otp

router = APIRouter()


class SendOtpRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


@router.post("/send-otp")
async def send_otp(data: SendOtpRequest):
    otp = await create_email_otp(data.email)

    return {
        "message": "OTP generated successfully",
        "otp": otp,  
        "expires_in": 300,
    }


@router.post("/verify-otp")
async def verify_otp(data: VerifyOtpRequest):
    await verify_email_otp(data.email, data.otp)

    return {"message": "Email verified successfully"}

import os

APP_ENV = os.getenv("APP_ENV", "production")  
