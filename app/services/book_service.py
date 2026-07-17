from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.book import BookCreate, BookUpdate
from app.models.book import Book
from app.repositories.book_repository import BookRepository
from app.core.exceptions import BookNotFoundException

class BookService:
    """Service class handling all business logic for the book catalog."""

    @staticmethod
    async def get_all(
        session: AsyncSession,
        page: int,
        size: int,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
        price_range: list[int] | None = None
    ):
        """
        Retrieves a paginated and filtered list of books from the catalog.

        Args:
            session (AsyncSession): The asynchronous database session.
            page (int): The page number to retrieve (1-indexed).
            size (int): The number of books per page.
            title (str | None, optional): Filter by book title (partial match). Defaults to None.
            author (str | None, optional): Filter by author name (partial match). Defaults to None.
            year (int | None, optional): Filter by publication year. Defaults to None.
            price_range (list[int] | None, optional): Filter by a price range [min_price, max_price]. Defaults to None.

        Returns:
            dict: A paginated response containing a list of Book objects and metadata.
        """
        repo = BookRepository(session)
        return await repo.get_all(title=title, page=page, size=size, author=author, year=year, price_range=price_range)
     
    @staticmethod
    async def get_book_by_id(session: AsyncSession, book_id: int, lock_for_update: bool = False) -> Book:
        """
        Retrieves a single book by its ID.

        Args:
            session (AsyncSession): The asynchronous database session.
            book_id (int): The ID of the book to retrieve.
            lock_for_update (bool, optional): If True, applies a database-level "FOR UPDATE" lock 
                                              on the row to prevent concurrent modifications. Defaults to False.

        Returns:
            Book: The retrieved Book model instance.

        Raises:
            BookNotFoundException: If no book exists with the provided ID.
        """
        repo = BookRepository(session)
        result = await repo.get_by_id(book_id, lock_for_update)
        if not result:
            raise BookNotFoundException()
        return result

    @staticmethod   
    async def create_book(session: AsyncSession, book_in: BookCreate) -> Book:
        """
        Creates a new book entry in the catalog.

        Args:
            session (AsyncSession): The asynchronous database session.
            book_in (BookCreate): The validated Pydantic schema containing the new book's data.

        Returns:
            Book: The newly created Book model instance.
        """
        new_book = Book(**book_in.model_dump())
        repo = BookRepository(session)
        return await repo.create(new_book)

    @staticmethod
    async def update_book(session: AsyncSession, book_id: int, book_in: BookUpdate) -> Book:
        """
        Partially updates an existing book's details.

        Only fields explicitly provided in the `book_in` schema will be updated; 
        unset fields are ignored.

        Args:
            session (AsyncSession): The asynchronous database session.
            book_id (int): The ID of the book to update.
            book_in (BookUpdate): The validated Pydantic schema containing the fields to update.

        Returns:
            Book: The updated Book model instance.

        Raises:
            BookNotFoundException: If the book to update does not exist.
        """
        book = await BookService.get_book_by_id(session, book_id)
        updated_data = book_in.model_dump(exclude_unset=True) 
        for key, value in updated_data.items():
            setattr(book, key, value)
        repo = BookRepository(session)
        return await repo.update(book)

    @staticmethod
    async def delete_book(session: AsyncSession, book_id: int):
        """
        Removes a book from the catalog.

        Args:
            session (AsyncSession): The asynchronous database session.
            book_id (int): The ID of the book to delete.

        Returns:
            Book: The deleted Book model instance (or confirmation of deletion, depending on repo).

        Raises:
            BookNotFoundException: If the book to delete does not exist.
        """
        book = await BookService.get_book_by_id(session, book_id)
        repo = BookRepository(session)
        return await repo.delete(book)