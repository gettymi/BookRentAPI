from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.user_services import UserService

# Цей об'єкт шукає токен у заголовку Authorization (Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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


    
    # КРОК 1: Спробуй розкодувати токен за допомогою jwt.decode()
    # (Використовуй settings.SECRET_KEY та settings.ALGORITHM)
    # Згорни це у блок try...except JWTError: щоб зловити невалідні токени.
    
    # КРОК 2: Дістань email (ключ 'sub') з розкодованого словника (payload).
    # Якщо email відсутній, викидай credentials_exception.
    
    # КРОК 3: Знайди користувача в базі за цим email через UserService.
    # Якщо користувача немає, викидай credentials_exception.
    
    # КРОК 4: Поверни об'єкт користувача.
    