from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.book import BookCreate, BookResponse,BookUpdate
from app.models.book import Book
from app.core.database import get_db


router = APIRouter()


@router.post("/", response_model=BookResponse)
async def create_book(
    book_in: BookCreate,           
    session: AsyncSession = Depends(get_db) 
):
    new_book = Book(**book_in.model_dump())

    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)

    return new_book
    


@router.get("/",response_model=list[BookResponse])
async def show_book(
    session: AsyncSession = Depends(get_db)
):
    query = select(Book)

    result = await session.execute(query)

    return result.scalars().all()


@router.get("/{book_id}",response_model=BookResponse)
async def show_book_id(
        book_id: int,
        session: AsyncSession = Depends(get_db)
):
    
    query = select(Book).where(Book.id == book_id)

    result = await session.execute(query)

    book = result.scalar_one_or_none()

    if book:
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")
    
@router.patch("/{book_id}",response_model=BookResponse)
async def update_book(
        book_id: int,
        book_in: BookUpdate,
        session: AsyncSession = Depends(get_db)
):  
    query = select(Book).where(Book.id == book_id)

    result = await session.execute(query)

    book = result.scalar_one_or_none()

    if book:
        updated_data = book_in.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(book,key,value)

        await session.commit()
        await session.refresh(book)

        return book

    else:
        raise HTTPException(status_code=404,detail="Book to change not found")

    