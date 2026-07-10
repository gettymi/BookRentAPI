from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.book import BookCreate, BookUpdate
from app.models.book import Book
from app.repositories.book_repository import BookRepository
from app.core.exceptions import BookNotFoundException

class BookService:
     @staticmethod
     async def get_all(session: AsyncSession, title: str | None = None):
      repo = BookRepository(session)
      return await repo.get_all(title=title)
     
     @staticmethod
     async def get_book_by_id(session: AsyncSession, book_id: int, lock_for_update: bool = False):
      repo = BookRepository(session)
      result = await repo.get_by_id(book_id, lock_for_update)
      if not result:
         raise BookNotFoundException()
      return result

     @staticmethod   
     async def create_book(session: AsyncSession, book_in: BookCreate):
        new_book = Book(**book_in.model_dump())
        repo = BookRepository(session)
        return await repo.create(new_book)

     @staticmethod
     async def update_book(session: AsyncSession, book_id: int, book_in: BookUpdate):
        book = await BookService.get_book_by_id(session, book_id)
        updated_data = book_in.model_dump(exclude_unset=True) 
        for key, value in updated_data.items():
            setattr(book, key, value)
        repo = BookRepository(session)
        return await repo.update(book)

     @staticmethod
     async def delete_book(session: AsyncSession, book_id: int):
        book = await BookService.get_book_by_id(session, book_id)
        repo = BookRepository(session)
        return await repo.delete(book)

