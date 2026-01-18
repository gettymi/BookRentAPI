class BookService:
     @staticmethod
     async def get_all(session: AsyncSession, title: str | None = None):
        query = select(Book)
        if title:
            query = query.where(Book.title.ilike(f"%{title}%"))
        
        result = await session.execute(query)
        return result.scalars().all()
     
     @staticmethod
     async def get_book_by_id(session: AsyncSession, book_id: int):
        query = select(Book).where(Book.id == book_id)
        result = await session.execute(query)
        book = result.scalar_one_or_none()
        if book:
            return book
        else:
            raise HTTPException(status_code=404, detail="Book not found")
        

     @staticmethod   
     async def create_book(session: AsyncSession, book_in: BookCreate):
        new_book = Book(**book_in.model_dump())
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

     @staticmethod
     async def update_book(session: AsyncSession, book_id: int, book_in: BookUpdate):
        book = await BookService.get_book_by_id(session, book_id)
        updated_data = book_in.model_dump(exclude_unset=True) 
        for key, value in updated_data.items():
            setattr(book, key, value)
        await session.commit()
        await session.refresh(book)
        return book
     
     @staticmethod
     async def delete_book(session: AsyncSession, book_id: int):
        book = await BookService.get_book_by_id(session, book_id)
        await session.delete(book)
        await session.commit()
        return book
