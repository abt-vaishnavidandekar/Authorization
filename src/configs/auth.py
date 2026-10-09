from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import JSONResponse
from fastapi import status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from configs.security import ALGORITHM, SECRET_KEY
from configs.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/login")


async def get_current_user(
    access_token: str = Depends(oauth2_scheme), db:AsyncSession=Depends(get_db)):

    if not access_token:
        return JSONResponse(
            status_code = status.HTTP_401_UNAUTHORIZED,
            content={
                "success" : False,
                "msg" : "Invalid Access token"
            }
        )

    try:

        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        role = payload.get("role")
        token_type = payload.get("type")

        if not user_id or not role:
            return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        contentc= {
                            "success" : False,
                            "msg" : "Invalid Access token"
                        }
                    )

        if token_type != "access":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content= {
                    "success" : False,
                    "msg" : "Invalid Access token"
                }
            )

        return {
            "user_id": int(user_id),
            "role": role
        }

    except JWTError:

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content= {
                "success" : False,
                "msg" : "Invalid Access token"
            }
        )

