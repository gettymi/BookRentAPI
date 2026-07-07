from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from app.core.config import settings
import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_in_bytes = plain_password.encode('utf-8')
    hashed_password_in_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_in_bytes, hashed_password_in_bytes)

def get_password_hash(password: str) -> str:
    password_in_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt() 
    hashed_password = bcrypt.hashpw(password_in_bytes, salt).decode('utf-8')
    return hashed_password

def create_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt    
