import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from httpx import AsyncClient, ASGITransport
import pytest
from app.main import app 
from app.core.database import Base, get_db  
from app.core.config import settings

TEST_DATABASE_URL = f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@db:5432/bookrentapi_test'

test_engine = create_async_engine(TEST_DATABASE_URL,echo=True)

test_session_local = async_sessionmaker(test_engine,class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_database():

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield 

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def async_client():

    async def override_get_db():
        async with test_session_local() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()
