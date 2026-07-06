from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.database import get_db
from app.models import User
from app.services.user_services import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(get_db)):
    return await UserService.create_user(session,user_in)


@router.patch("/{user_id}",response_model=UserResponse)
async def update_user(user_in: UserUpdate,user_id: int, session: AsyncSession = Depends(get_db)):
    return await UserService.update_user(session,user_in,user_id)
