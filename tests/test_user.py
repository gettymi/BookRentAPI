import pytest
from httpx import AsyncClient
from typing import Any
from app.models import User
from tests.conftest import TestingSessionLocal
from tests.test_rentals import helper_create_user
from app.core.dependencies import get_current_user
from app.main import app

@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(async_client: AsyncClient) -> None:

    user_in = {
        "email":"testuser@ex.com",
        "password":"qwerty12345W",
    }

    response = await async_client.post("/users/",json=user_in)

    assert response.status_code == 201

@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_with_used_email(async_client: AsyncClient) -> None:

    user_in = {
        "email":"testuser@ex.com",
        "password":"qwerty12345",
    }

    response = await async_client.post("/users/",json=user_in)

    assert response.status_code == 201

    another_response = await async_client.post("/users/",json=user_in)

    assert another_response.status_code == 400

@pytest.mark.asyncio(loop_scope="session")
async def test_update_user(async_client: AsyncClient, setup_database:Any) -> None:


    new_user = await helper_create_user(setup_database)

    data = {
        "email":"newmail@to.com",
        "password":"123456789WDQ"
    }

    response = await async_client.patch(f"/users/{new_user.id}",json=data)

    assert response.status_code == 200

    app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_wrong_id(async_client: AsyncClient, setup_database:Any) -> None:

    new_user = await helper_create_user(setup_database)

    data = {
        "email":"newmail@to.com"
    }

    response = await async_client.patch(f"/users/{3}",json=data)

    assert response.status_code == 404

    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_profile(async_client: AsyncClient, setup_database:Any) -> None:

    new_user = await helper_create_user(setup_database)

    response = await async_client.get("/users/me")

    assert response.status_code == 200

    app.dependency_overrides.pop(get_current_user, None)