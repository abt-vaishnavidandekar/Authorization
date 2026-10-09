from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi import FastAPI
from configs.redis import close_redis

from src.routers.admin import admin_router
from src.routers.auth import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()


app = FastAPI(lifespan=lifespan)

app.include_router(admin_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v3")

@app.get("/")
async def get():
    return {"Msg" : "Api running properly"}

