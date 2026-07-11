from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.book import BookCreate, BookResponse,BookUpdate, BookCatalogResponse
from app.schemas.user import UserResponse
from app.schemas.pagination import PaginatedResponse
from app.models.user import User
from app.models.book import Book
from app.core.database import get_db
from app.services.book_service import BookService
from app.core.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/",response_model=PaginatedResponse[BookCatalogResponse])
async def get_books(
    page: int = 1,
    size: int = 50,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    price_range: list[int] | None = Query(default=None),
    session: AsyncSession = Depends(get_db)
):
    return await BookService.get_all(session=session,page=page,size=size,title=title,author=author,year=year,price_range=price_range) 

@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(
    book_in: BookCreate,           
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    print(f"Book created by user: {current_user.email}")
    return await BookService.create_book(session, book_in)


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
        current_user: User = Depends(get_current_admin_user)
):  
    return await BookService.update_book(session,book_id,book_in)

@router.delete("/{book_id}", status_code=204)
async def delete_book(
        book_id: int,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):  
    return await BookService.delete_book(session,book_id)
    
 
    