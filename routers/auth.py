from fastapi import APIRouter, Depends
from schema import UserCreateRequest
from models import User
from connection import get_async_session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select


router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

@router.post("/auth")
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

async def authentication_user(user_name, hashed_password, session):
    statement = select(User).where(User.user_name == user_name) #user_name is unique 
    result = await session.execute(statement)
    user = result.scalars().first()
    if not user:
        return False
    if not bcrypt_context.verify(hashed_password,user.hashed_password):
        return False
    return True


@router.post("/token")
async def get_token_api(
    body: OAuth2PasswordRequestForm= Depends(), session = Depends(get_async_session)
):
    user = await authentication_user(body.username, body.password, session)
    if not user:
        return False
    return True