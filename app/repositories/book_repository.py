from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.book import Book

class BookRepository:

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self,
      page: int,
      size: int,
      title: str | None = None,
      author: str | None = None,
      year: int | None = None,
      price_range: list[int] | None = None
      ):

      query = select(Book.title, Book.author,Book.year,Book.price, func.count(Book.id).label("available_count"), func.min(Book.id).label("book_id"))
      total_query = select(func.count(func.distinct(Book.title)))


      if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
        total_query = total_query.where(Book.title.ilike(f"%{title}%"))
      if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
        total_query = total_query.where(Book.author.ilike(f"%{author}%"))
      if year:
        query = query.where(Book.year == year)
        total_query = total_query.where(Book.year == year)
      if price_range:
        query = query.where(Book.price.between(price_range[0], price_range[1]))
        total_query = total_query.where(Book.price.between(price_range[0], price_range[1]))

      query = query.group_by(Book.title,Book.author,Book.year, Book.price)
      query = query.offset((page - 1)* size).limit(size)
    
      result = await self.session.execute(query) 
      total_result =  await self.session.execute(total_query)

      selected_books =  result.mappings().all()
      total = total_result.scalar_one()
      return {"items": selected_books, "size": size, "page": page, "total":total}

    async def get_by_id(self, book_id: int, lock_for_update: bool = False):
        if not lock_for_update:
            query = select(Book).where(Book.id == book_id)
        else:
            query = select(Book).where(Book.id == book_id).with_for_update()
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
     
    
