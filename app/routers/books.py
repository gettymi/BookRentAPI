from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.book import BookCreate, BookResponse,BookUpdate
from app.models.book import Book
from app.core.database import get_db
from app.services.book_service import BookService

router = APIRouter()


@router.post("/", response_model=BookResponse)
async def create_book(
    book_in: BookCreate,           
    session: AsyncSession = Depends(get_db) 
):
    return await BookService.create_book(session, book_in)
    


@router.get("/",response_model=list[BookResponse])
async def get_books(
    title: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    return await BookService.get_all(session,title) 



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
        session: AsyncSession = Depends(get_db)
):  
    return await BookService.update_book(session,book_id,book_in)

@router.delete("/{book_id}",response_model=BookResponse)
async def delete_book(
        book_id: int,
        session: AsyncSession = Depends(get_db)
):  
    return await BookService.delete_book(session,book_id)
    
 
    