from fastapi import APIRouter, Depends
from schema import UserCreateRequest
from models import User
from connection import get_async_session
from passlib.context import CryptContext

router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

@router.post("/auth")
async def create_user_api(
    body:UserCreateRequest, session = Depends(get_async_session)
):
    user = User(
        hashed_password = bcrypt_context.hash(body.hashed_password),
        user_name = body.user_name,
        email = body.user_name,
        role = body.role,
        is_active = True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user