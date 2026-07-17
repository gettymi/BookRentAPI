from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from app.core.config import settings
import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password using bcrypt.

    Args:
        plain_password (str): The raw password provided by the user (e.g., during login).
        hashed_password (str): The bcrypt-hashed password stored in the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    password_in_bytes = plain_password.encode('utf-8')
    hashed_password_in_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_in_bytes, hashed_password_in_bytes)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt with an automatically generated salt.

    Args:
        password (str): The raw password to hash (e.g., during registration).

    Returns:
        str: The fully hashed password, ready to be stored in the database.
    """
    password_in_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt() 
    hashed_password = bcrypt.hashpw(password_in_bytes, salt).decode('utf-8')
    return hashed_password

def create_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Generates a JSON Web Token (JWT) for user authentication.

    The token payload includes the subject (usually the user's ID) and an 
    expiration timestamp. If no custom expiration delta is provided, it defaults 
    to the ACCESS_TOKEN_EXPIRE_MINUTES defined in the application settings.

    Args:
        subject (Union[str, Any]): The identifier to embed in the token (typically user ID).
        expires_delta (timedelta, optional): Custom expiration duration. Defaults to None.

    Returns:
        str: The encoded JWT as a string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt