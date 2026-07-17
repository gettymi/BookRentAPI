from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user
from sqlalchemy import select, func
from app.models import User, Rental, Book
from app.services.book_service import BookService
from datetime import datetime, timedelta, timezone
from app.core.logger import logger
from app.core.exceptions import (
    BookNotAvailableException, 
    TooLongRentalDaysException, 
    UserHasOverdueBooksException, 
    RentalNotFoundException, 
    PermissionDeniedException, 
    BookAlreadyReturnedException, 
    MaxRentalsReachedException, 
    InvalidRentalDurationException
)

class RentalService:
    """Service class handling all business logic for book rentals."""

    @staticmethod
    async def rent_book(session: AsyncSession, book_id: int, rental_days: int, current_user: User) -> Rental:
        """
        Creates a new book rental for a user, enforcing all business rules.

        Checks if the requested duration is valid, the book is available, the user
        has no overdue books, and the user hasn't reached their active rental limit.

        Args:
            session (AsyncSession): The asynchronous database session.
            book_id (int): The ID of the book to rent.
            rental_days (int): The number of days the user wants to rent the book.
            current_user (User): The authenticated user making the request.

        Returns:
            Rental: The newly created rental record.

        Raises:
            InvalidRentalDurationException: If rental_days is <= 0 or > 90.
            BookNotAvailableException: If the requested book is currently rented out.
            UserHasOverdueBooksException: If the user currently has unreturned, overdue books.
            MaxRentalsReachedException: If the user already has 3 active rentals.
            Exception: If a database commit fails.
        """
        if rental_days <= 0 or rental_days > 90: 
            raise InvalidRentalDurationException()

        book = await BookService.get_book_by_id(session, book_id, lock_for_update=True) 

        if not book.is_available:
            raise BookNotAvailableException()

        overdue_queries = select(Rental).where(
            Rental.user_id == current_user.id,
            Rental.returned_at.is_(None),
            Rental.due_date < datetime.now(timezone.utc).replace(tzinfo=None)
        )

        result = await session.execute(overdue_queries)
        overdue_rentals = result.scalars().all()

        if overdue_rentals:
            raise UserHasOverdueBooksException()
        
        user_queries = select(func.count(Rental.id)).where(
            Rental.user_id == current_user.id,
            Rental.returned_at.is_(None),
        )

        user_rents = await session.scalar(user_queries)

        if user_rents >= 3:
            raise MaxRentalsReachedException()

        due_date = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=rental_days)
        total_price = RentalService.calculate_rental_cost(rental_days)
        new_rent = Rental(user_id=current_user.id, book_id=book_id, due_date=due_date, total_price=total_price)
        session.add(new_rent)
        book.is_available = False 

        logger.info(f"User {current_user.id} is attempting to rent Book {book_id} for {rental_days} days.")

        try:
            await session.commit()
            await session.refresh(new_rent)
            return new_rent 
        except Exception as e:
            await session.rollback()
            raise e

    @staticmethod
    def calculate_rental_cost(rental_days: int) -> float:
        """
        Calculates the total cost of a rental based on dynamic pricing tiers.

        Args:
            rental_days (int): The number of days the book will be rented.

        Returns:
            float: The calculated total price.

        Raises:
            TooLongRentalDaysException: If the rental period exceeds the maximum allowed tier (365 days).
        """
        tier1 = 5
        tier2 = 14
        tier3 = 31
        tier4 = 365

        if rental_days <= tier1:
            return rental_days * 1.50
        elif tier1 < rental_days <= tier2:
            return rental_days * 1.25
        elif tier2 < rental_days <= tier3:
            return rental_days * 1
        elif tier3 < rental_days <= tier4:
            return rental_days * 0.9
        else:
            raise TooLongRentalDaysException()
    
    @staticmethod
    async def return_book(session: AsyncSession, rental_id: int, current_user: User, is_damaged: bool = False) -> Rental:
        """
        Processes the return of a rented book, calculating any late or damage fees.

        Args:
            session (AsyncSession): The asynchronous database session.
            rental_id (int): The ID of the rental to return.
            current_user (User): The authenticated user returning the book.
            is_damaged (bool, optional): Whether the book is being returned damaged. Defaults to False.

        Returns:
            Rental: The updated rental record with the calculated final price.

        Raises:
            RentalNotFoundException: If the rental_id does not exist.
            PermissionDeniedException: If the user is trying to return someone else's rental.
            BookAlreadyReturnedException: If the rental has already been completed.
            Exception: If a database commit fails.
        """
        query = select(Rental).where(Rental.id == rental_id)
        result = await session.execute(query)
        rental = result.scalar_one_or_none()

        if not rental:
            raise RentalNotFoundException()

        if not rental.user_id == current_user.id:
            raise PermissionDeniedException()
        
        if rental.returned_at:
            raise BookAlreadyReturnedException()

        rental.returned_at = datetime.now(timezone.utc).replace(tzinfo=None)

        # Calculate late fee
        if rental.returned_at > rental.due_date:
            rental.total_price += min(2 * float(((rental.returned_at - rental.due_date).total_seconds())) / 86_400, 100)
        
        # Calculate damage fee
        if is_damaged:
            rental.total_price += 15
            
        book = await BookService.get_book_by_id(session, rental.book_id)

        book.is_available = True 
        rental.status = "returned"

        logger.info(f"User {current_user.id} returned Book {rental.book_id}. Damage reported: {is_damaged}. Total fee: ${rental.total_price:.2f}")

        try:
            await session.commit()
            await session.refresh(rental)
            return rental
        except Exception as e:
            await session.rollback()
            raise e 

    @staticmethod
    async def get_user_rentals(
        session: AsyncSession, 
        user_id: int, 
        current_user: User,
        size: int,
        page: int, 
        status: str | None = None,
        end_date: datetime | None = None,
        start_date: datetime | None = None,
    ) -> dict:
        """
        Retrieves a paginated and filtered list of rentals for a specific user.

        Args:
            session (AsyncSession): The asynchronous database session.
            user_id (int): The ID of the user whose rentals are being fetched.
            current_user (User): The user making the request (must match user_id or be admin).
            size (int): The number of records to return per page.
            page (int): The page number to retrieve.
            status (str | None, optional): Filter by rental status. Defaults to None.
            end_date (datetime | None, optional): Filter by due dates before this time. Defaults to None.
            start_date (datetime | None, optional): Filter by rental dates after this time. Defaults to None.

        Returns:
            dict: A dictionary containing "items" (list of Rentals), "page", "size", and "total" count.

        Raises:
            PermissionDeniedException: If a standard user attempts to view another user's rentals.
            Exception: If a database transaction fails.
        """
        if current_user.id != user_id and not current_user.is_superuser:
            raise PermissionDeniedException()
            
        query = select(Rental).where(Rental.user_id == user_id)
        total_query = select(func.count(Rental.id)).where(Rental.user_id == user_id)

        if status:
            query = query.where(Rental.status == status)
            total_query = total_query.where(Rental.status == status)
        if start_date:
            query = query.where(Rental.rented_at >= start_date)
            total_query = total_query.where(Rental.rented_at >= start_date)
        if end_date:
            query = query.where(Rental.due_date <= end_date)
            total_query = total_query.where(Rental.due_date <= end_date)

        query = query.offset((page - 1) * size).limit(size)

        try:
            result = await session.execute(query)
            total_result = await session.execute(total_query)
            user_rentals = result.scalars().all()
            total = total_result.scalar_one()
        except Exception as e:
            await session.rollback()
            raise e

        return {"items": user_rentals, "page": page, "size": size, "total": total}

    @staticmethod
    async def get_overdue_rentals(session: AsyncSession) -> list[Rental]:
        """
        Retrieves all currently overdue rentals across the entire system.
        
        Intended for admin use to track down unreturned books.

        Args:
            session (AsyncSession): The asynchronous database session.

        Returns:
            list[Rental]: A list of all Rental records where the due date has passed 
                          and the book has not been returned.
        """
        query = select(Rental).where(
            Rental.due_date < datetime.now(timezone.utc).replace(tzinfo=None),
            Rental.returned_at.is_(None)
        )
        result = await session.execute(query)

        return list(result.scalars().all())