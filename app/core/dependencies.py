from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.user_services import UserService
from app.schemas.user import UserResponse
from app.core.exceptions import CredentialsException, PermissionDeniedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
):
    credentials_exception = CredentialsException()
    try:
        payload = jwt.decode(token,settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        email = payload.get('sub')
        if not email:
            raise credentials_exception
        user = await UserService.find_user(session, email)

        if not user:
            raise credentials_exception 
        
        return user 

    except JWTError:
        raise credentials_exception

async def get_current_admin_user(
    user: UserResponse = Depends(get_current_user)
):
    if user.is_superuser:
        return user 
    raise PermissionDeniedException()
    
