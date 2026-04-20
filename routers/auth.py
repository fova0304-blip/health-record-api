from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from schema import UserCreateRequest, Token
from models import User
from connection import get_async_session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select
from jose import jwt, JWTError
import os
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix = "/auth",
    tags= ["auth"]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = "auth/token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

@router.post("/")
async def create_user_api(
    body:UserCreateRequest, session = Depends(get_async_session)
):
    user = User(
        hashed_password = bcrypt_context.hash(body.hashed_password),
        user_name = body.user_name,
        email = body.email,
        role = body.role,
        is_active = True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def authenticate_user(user_name, hashed_password, session):
    statement = select(User).where(User.user_name == user_name) #user_name is unique 
    result = await session.execute(statement)
    user = result.scalars().first()
    if not user:
        return False
    if not bcrypt_context.verify(hashed_password,user.hashed_password):
        return False
    return user

def get_access_token(user_name:str, user_id:int, role:str ,expire_time:timedelta):
    encode = {"user_name": user_name, "user_id" : user_id, "role": role, "exp": datetime.now(timezone.utc)+expire_time}
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], session:AsyncSession=Depends(get_async_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name:str = payload.get("user_name")
        user_id:int = payload.get("user_id")
        role:str = payload.get("role")
        if user_name is None or user_id is None:
            raise HTTPException(status_code=401, detail="can not find the user")
        statement = select(User).where(User.user_id == user_id)
        result = await session.execute(statement)
        user = result.scalars().first()
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="can not find the user")

@router.post("/token", response_model=Token)
async def get_token_api(
    body: OAuth2PasswordRequestForm= Depends(), session = Depends(get_async_session)
):
    user = await authenticate_user(body.username, body.password, session)
    if not user:
        return False
    token = get_access_token(user.user_name, user.user_id, user.role, expire_time=timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}