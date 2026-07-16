import pytest
from datetime import datetime,timedelta,timezone
from httpx import AsyncClient
from typing import Any
from app.models import User,Book,Rental
from tests.conftest import TestingSessionLocal
from app.core.security import get_password_hash
from app.core.dependencies import get_current_user
from app.main import app


async def helper_create_user(setup_database: Any,is_superuser:bool = True) -> User:

    hashed_password = get_password_hash("strongpas")
    new_user = User(email="test@wp.pl", hashed_password=hashed_password, is_superuser=is_superuser)
    
    async with TestingSessionLocal() as session:
        session.add(new_user)
        await session.commit()

    app.dependency_overrides[get_current_user] = lambda: new_user

    return new_user

async def helper_create_book(setup_database: Any, is_available: bool = True) -> Book:

    new_book = Book(title="1984", year=2023, author='George Orwell', price=700, is_available=is_available)

    async with TestingSessionLocal() as session:
        session.add(new_book)

        await session.commit()
        await session.refresh(new_book)

    return new_book


@pytest.mark.asyncio(loop_scope="session")
async def test_rent_book_flow(async_client: AsyncClient, setup_database: Any) -> None:
    
    await helper_create_user(setup_database=setup_database)
    new_book = await helper_create_book(setup_database=setup_database)
    
    data = {
        "book_id":new_book.id,
        "rental_days":15
    }

    response = await async_client.post("/rentals/",params=data)
    
    assert response.status_code == 200
    
    assert "due_date" in response.json()
    
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio(loop_scope="session")
async def test_not_available_rent(async_client: AsyncClient, setup_database: Any) -> None:

    await helper_create_user(setup_database=setup_database)
    new_book = await helper_create_book(setup_database=setup_database, is_available=False)

    params = {
        "book_id":new_book.id,
        "rental_days":15
    }

    response = await async_client.post("/rentals/",params=params)
    
    assert response.status_code == 409
    
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio(loop_scope="session")
async def test_max_rentals_reach(async_client: AsyncClient, setup_database: Any) -> None:
    await helper_create_user(setup_database=setup_database)

    for i in range(4):
        new_book = await helper_create_book(setup_database=setup_database)
        params = {
            "book_id":new_book.id,
            "rental_days":12
        }
        response = await async_client.post("/rentals/",params=params)
    
    assert response.status_code == 403

    app.dependency_overrides.pop(get_current_user, None)

    

@pytest.mark.asyncio(loop_scope="session")
async def test_user_has_overdue(async_client: AsyncClient, setup_database: Any) -> None:

    new_user = await helper_create_user(setup_database=setup_database)
    new_book = await helper_create_book(setup_database=setup_database)
    new_rent = Rental(
        user_id=new_user.id,
        book_id=new_book.id,
        rented_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=10),
        due_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=5),
        total_price = 100
    )

    async with TestingSessionLocal() as session:
        session.add(new_rent)
        await session.commit()
    
    another_new_book = await helper_create_book(setup_database=setup_database)

    params = {
        "book_id":new_book.id,
        "rental_days":15
    }

    response = await async_client.post("/rentals/",params=params)

    assert response.status_code == 403

    app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio(loop_scope="session")
async def test_invalid_rental_duration(async_client: AsyncClient, setup_database: Any) -> None:
    await helper_create_user(setup_database=setup_database)
    new_book = await helper_create_book(setup_database=setup_database)

    params = {
        "book_id": new_book.id,
        "rental_days": 100
    }



    response = await async_client.post("/rentals/",params=params)

    assert response.status_code == 400
    

    app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio(loop_scope="session")
async def test_return_book_flow(async_client: AsyncClient, setup_database: Any) -> None:

    await helper_create_user(setup_database=setup_database)
    new_book = await helper_create_book(setup_database=setup_database)

    params = {
        "book_id": new_book.id,
        "rental_days": 15
    }

    response = await async_client.post("/rentals/",params=params)

    rental_id = response.json()["id"]

    async with TestingSessionLocal() as session:
        refreshed_book = await session.get(Book,new_book.id)
    assert refreshed_book.is_available == False

    ret_response = await async_client.post(f"/rentals/{rental_id}/return")

    async with TestingSessionLocal() as session:
        refreshed_book = await session.get(Book,new_book.id)
    assert refreshed_book.is_available == True

    assert ret_response.json()["returned_at"]

    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_rentals(async_client: AsyncClient, setup_database: Any) -> None:

    await helper_create_user(setup_database=setup_database)

    params = {
        "start_date":"2026-01-01", 
        "status":"active",
        "end_date":"2026-12-31",
        "size":5,
        "page":1,
    }

    response = await async_client.get("/rentals/me",params=params)

    assert response.status_code == 200

    app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio(loop_scope="session")
async def test_get_overdue_rentals(async_client: AsyncClient, setup_database: Any) -> None:

    await helper_create_user(setup_database=setup_database)

    response = await async_client.get("/rentals/overdue")

    assert response.status_code == 200

    app.dependency_overrides.pop(get_current_user, None)