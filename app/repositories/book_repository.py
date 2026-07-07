from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.book import Book

class BookRepository:

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self, title: str | None = None):
        query = select(Book)
        if title:
            query = query.where(Book.title == title)
        result = await self.session.execute(query) 
        return result.scalars().all()

    async def get_by_id(self, book_id: int):
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, new_book: Book):
        self.session.add(new_book)
        await self.session.commit()
        await self.session.refresh(new_book)
        return new_book

    async def update(self, new_book: Book):
        await self.session.commit()
        await self.session.refresh(new_book)
        return new_book
     
    async def delete(self, new_book: Book):
        await self.session.delete(new_book)
        await self.session.commit()
        return new_book
     
    
