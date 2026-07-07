from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:

    @staticmethod
    async def create_user(session: AsyncSession, user_in: UserCreate):


        query = select(User).where(User.email == user_in.email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            raise HTTPException(status_code=400, detail="Email already registered")

        raw_password = user_in.password
        hashed_pass = get_password_hash(raw_password)

        user_data = user_in.model_dump(exclude ={"password"})

        new_user = User(**user_data,hashed_password=hashed_pass)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def update_user(session: AsyncSession, user_in: UserUpdate,user_id:int):
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
             raise HTTPException(status_code=404, detail="User not found")


        updated_data = user_in.model_dump(exclude_unset=True)

        if 'password' in updated_data:
            hashed = get_password_hash(updated_data['password'])

            user.hashed_password = hashed

            del updated_data['password']
        
            for key, value in updated_data.items():
                setattr(user,key,value)

        await session.commit()
        await session.refresh(user)

        return user
    
    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str):
        user = await UserService.find_user(session,email)
        if not user or not verify_password(plain_password=password, hashed_password=user.hashed_password):
            return None

        return user
    
    @staticmethod
    async def find_user(session: AsyncSession, email: str):
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()


    
