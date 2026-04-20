from fastapi import APIRouter, Depends, HTTPException
from connection import get_async_session
from .auth import get_current_user
from sqlalchemy import select
from models import User
from schema import UserResponse

router = APIRouter(
    prefix= "/admin",
    tags = ["admin"]
)

@router.get("/admin/", response_model=list[UserResponse])
async def get_all_user_api(
    session = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized User")
    users = select(User)
    results = await session.execute(users)
    all_users = results.scalars().all()
    return all_users

@router.delete("/admin/delete/{user_id}")
async def delete_user_api(
    user_id:int,
    session = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Not Valid User")
    user = select(User).where(User.user_id == current_user.user_id)
    result = await session.execute(user)
    delete_user = result.scalars().first()
    await session.delete(delete_user) 
    await session.commit()
    return "User Deleted"


