from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from connection import get_async_session
from .auth import get_current_user
from models import User
from sqlalchemy import select
from schema import UserPasswordRequest
from schema import UserResponse

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

router = APIRouter(
    prefix="/user", 
    tags = ["user"]
)

@router.get("/", response_model=UserResponse)
async def get_user_info_api(
    session = Depends(get_async_session),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    statement = select(User).where(User.user_id == user.user_id)
    result = await session.execute(statement)
    user_info = result.scalars().first()
    return user_info

@router.put("/change-password")
async def change_user_password_api(
    body: UserPasswordRequest,
    session = Depends(get_async_session),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    
    statement = select(User).where(User.user_id == user.user_id)
    result = await session.execute(statement)
    user_info = result.scalars().first()

    if not bcrypt_context.verify(body.current_password, user_info.hashed_password):
        raise HTTPException(status_code=401, detail="Password Not Match")
    user_info.hashed_password = bcrypt_context.hash(body.new_password)
    await session.commit()
    await session.refresh(user_info)
    return "Password Updated"
    
@router.put("/change-phone-number")
async def change_phone_number_api(
    phone_number:str,
    session = Depends(get_async_session),
    user = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    
    statement = select(User).where(User.user_id == user.user_id)
    result = await session.execute(statement)
    user_info = result.scalars().first()

    user_info.phone_number = phone_number
    await session.commit()
    await session.refresh(user_info)
    return "Phone Number Updated"

