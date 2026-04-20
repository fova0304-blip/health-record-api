from fastapi import FastAPI
import models
from connection import engine
from contextlib import asynccontextmanager
from routers import crud, auth, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(crud.router)
app.include_router(admin.router)

