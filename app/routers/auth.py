from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.database import get_db
from app.services.user_services import UserService
from datetime import timedelta
from app.core.security import create_token
from app.core.config import settings
from app.schemas.token import Token


router = APIRouter()

@router.post("/login",response_model=Token)
async def login_for_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db)
):
    user = await UserService.authenticate_user(
        session= session,
        email= form_data.username,
        password=form_data.password 
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token(subject=user.email)

    refresh_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    refresh_token = create_token(
        subject=user.email,
        expires_delta=refresh_expires
    )
    
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

