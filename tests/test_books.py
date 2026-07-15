import pytest 
from app.main import app
from httpx import AsyncClient

from app.models.user import User
from app.core.dependencies import get_current_admin_user

@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_books_return_200(async_client: AsyncClient) -> None:
    response = await async_client.get("/books/")
    assert response.status_code == 200

    assert "items"  in response.json()

@pytest.mark.asyncio(loop_scope="session")
async def test_create_book(async_client: AsyncClient) -> None:

    fake_user =  User(id=1, email='admin@test.com' ,is_superuser=True)
    app.dependency_overrides[get_current_admin_user] = lambda: fake_user

    new_book_data = {
        "title": "The Pytest Guide",
        "author": "Bohdan",
        "year": 2024,
        "price": 1500,
    }

    response = await async_client.post("/books/", json=new_book_data)

    app.dependency_overrides.pop(get_current_admin_user, None)


    assert response.status_code == 201

@pytest.mark.asyncio(loop_scope="session")
async def test_get_unreal_book(async_client: AsyncClient) -> None:
    id = 999999
    response = await async_client.get(f"/books/{id}")
    assert response.status_code == 404

@pytest.mark.asyncio(loop_scope="session")
async def test_create_book_invalid_data(async_client: AsyncClient) -> None:

    fake_user =  User(id=1, email='admin@test.com' ,is_superuser=True)
    app.dependency_overrides[get_current_admin_user] = lambda: fake_user

    new_book_data = {
        "title": 123,
        "author": "Bohdan",
        "year": "1950",
        "price": 1500,
    }

    response = await async_client.post("/books/", json=new_book_data)

    app.dependency_overrides.pop(get_current_admin_user, None)

    assert response.status_code == 422
    
