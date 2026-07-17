from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service class handling user registration, updates, and authentication."""

    @staticmethod
    async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
        """
        Registers a new user in the system.

        Checks if the provided email is already in use. If not, hashes the password
        and creates a new user record.

        Args:
            session (AsyncSession): The asynchronous database session.
            user_in (UserCreate): The validated Pydantic schema containing user details.

        Returns:
            User: The newly created User model instance.

        Raises:
            HTTPException: 400 status code if the email is already registered.
        """
        query = select(User).where(User.email == user_in.email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            raise HTTPException(status_code=400, detail="Email already registered")

        raw_password = user_in.password
        hashed_pass = get_password_hash(raw_password)

        user_data = user_in.model_dump(exclude={"password"})

        new_user = User(**user_data, hashed_password=hashed_pass)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def update_user(session: AsyncSession, user_in: UserUpdate, user_id: int) -> User:
        """
        Updates an existing user's profile.

        Applies partial updates based on the provided schema. If a new password is 
        provided, it automatically hashes it before saving.

        Args:
            session (AsyncSession): The asynchronous database session.
            user_in (UserUpdate): The validated Pydantic schema with updated fields.
            user_id (int): The ID of the user to update.

        Returns:
            User: The updated User model instance.

        Raises:
            HTTPException: 404 status code if the user does not exist.
        """
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
             raise HTTPException(status_code=404, detail="User not found")

        updated_data = user_in.model_dump(exclude_unset=True)

        # Hash the new password if it is being updated
        if 'password' in updated_data:
            hashed = get_password_hash(updated_data['password'])
            user.hashed_password = hashed
            del updated_data['password']
        
        # Apply remaining updates (Fixed indentation here so it runs regardless of password update)
        for key, value in updated_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return user
    
    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
        """
        Authenticates a user against their email and plain-text password.

        Args:
            session (AsyncSession): The asynchronous database session.
            email (str): The email address of the user attempting to log in.
            password (str): The plain-text password to verify.

        Returns:
            User | None: The authenticated User object if credentials are correct, 
                         or None if authentication fails.
        """
        user = await UserService.find_user(session, email)
        if not user or not verify_password(plain_password=password, hashed_password=user.hashed_password):
            return None

        return user
    
    @staticmethod
    async def find_user(session: AsyncSession, email: str) -> User | None:
        """
        Looks up a user by their exact email address.

        Args:
            session (AsyncSession): The asynchronous database session.
            email (str): The email address to search for.

        Returns:
            User | None: The User model instance if found, otherwise None.
        """
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()