from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.user_services import UserService
from app.schemas.user import UserResponse
from app.core.exceptions import CredentialsException, PermissionDeniedException
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> User:
    """
    Validates the provided JWT token and retrieves the current authenticated user.

    This function acts as a FastAPI dependency. It extracts the Bearer token from 
    the request header, decodes it using the application's secret key, and searches 
    the database for the user associated with the token's subject (email).

    Args:
        token (str): The JWT Bearer token extracted from the Authorization header.
        session (AsyncSession): The asynchronous database session.

    Returns:
        User: The authenticated User model instance.

    Raises:
        CredentialsException: If the token is invalid, expired, malformed, or if 
                            the corresponding user no longer exists in the database.
    """
    credentials_exception = CredentialsException()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
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
    user: User = Depends(get_current_user)
) -> User:
    """
    Role-Based Access Control (RBAC) dependency for administrator endpoints.

    This dependency first runs `get_current_user` to authenticate the request, 
    then validates whether the authenticated user possesses superuser privileges.

    Args:
        user (User): The authenticated user, automatically injected by `get_current_user`.

    Returns:
        User: The authenticated administrator User model instance.

    Raises:
        PermissionDeniedException: If the authenticated user is not a superuser.
    """
    if user.is_superuser:
        return user 
    raise PermissionDeniedException()