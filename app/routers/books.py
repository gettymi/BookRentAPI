from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder
import json

from app.schemas.book import BookCreate, BookResponse,BookUpdate, BookCatalogResponse
from app.schemas.user import UserResponse
from app.schemas.pagination import PaginatedResponse
from app.models.user import User
from app.models.book import Book
from app.core.database import get_db
from app.services.book_service import BookService
from app.core.dependencies import get_current_admin_user
from app.core.redis import get_redis

router = APIRouter()


@router.get("/",response_model=PaginatedResponse[BookCatalogResponse])
async def get_books(
    page: int = 1,
    size: int = 50,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    price_range: list[int] | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    cache_key = f"books:page={page}:size={size}:title={title}:author={author}:year={year}:price={str(price_range)}"
    cached_query = await redis.get(cache_key)
    if cached_query:
        return json.loads(cached_query)

    db_result = await BookService.get_all(session=session,page=page,size=size,title=title,author=author,year=year,price_range=price_range) 
    await redis.setex(cache_key,60, json.dumps(jsonable_encoder(db_result)))
    return db_result

@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(
    book_in: BookCreate,           
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    redis: Redis = Depends(get_redis)
):
    new_book = await BookService.create_book(session, book_in)

    redis_keys = await redis.keys("books:*")
    if redis_keys:
        await redis.delete(*redis_keys)

    return new_book

@router.get("/{book_id}",response_model=BookResponse)
async def get_book_by_id(
        book_id: int,
        session: AsyncSession = Depends(get_db)
):
    return await BookService.get_book_by_id(session,book_id)    


@router.patch("/{book_id}",response_model=BookResponse)
async def update_book(
        book_id: int,
        book_in: BookUpdate,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_admin_user),
        redis: Redis = Depends(get_redis)
):  
    updated_book = await BookService.update_book(session,book_id,book_in)

    redis_keys = await redis.keys("books:*")
    if redis_keys:
        await redis.delete(*redis_keys)

    return updated_book

@router.delete("/{book_id}", status_code=204)
async def delete_book(
        book_id: int,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_admin_user),
        redis: Redis = Depends(get_redis)
):  
    deleted_book = await BookService.delete_book(session,book_id)
    redis_keys = await redis.keys("books:*")    
    if redis_keys:
        await redis.delete(*redis_keys)
    return None
 
    