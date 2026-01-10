from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase
import asyncio

engine = create_async_engine("postgresql+asyncpg://user:password@localhost/dbname",echo=True)


async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    


class Base(DeclarativeBase):
    pass
