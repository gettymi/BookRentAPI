import pytest
from httpx import AsyncClient
from typing import Any
from app.models import User
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio(loop_scope="session")
async def test_successful_login(async_client: AsyncClient, setup_database: Any) -> None:

    async with TestingSessionLocal() as session:
        hashed_pw = get_password_hash("strongpassword123")
        test_user = User(
            email="testuser@example.com",
            hashed_password=hashed_pw
        )
        session.add(test_user)
        await session.commit()


    login_data = {
        "username": "testuser@example.com",
        "password": "strongpassword123",
        "grant_type": "password" 
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = await async_client.post("/auth/login", data=login_data, headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    
