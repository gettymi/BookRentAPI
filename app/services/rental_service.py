from sqlalchemy.ext.asyncio import AsyncSession, Depends
from app.core.dependencies import get_current_user
from sqlalchemy import select, func
from app.models import User, Rental, Book
from app.services.book_service import BookService
from datetime import datetime, timedelta, timezone
from app.core.exceptions import BookNotAvailableException, TooLongRentalDaysException, UserHasOverdueBooksException, RentalNotFoundException, PermissionDeniedException, BookAlreadyReturnedException, MaxRentalsReachedException, InvalidRentalDurationException

class RentalService:

    @staticmethod
    async def rent_book(session: AsyncSession, book_id: int, rental_days : int, current_user: User):
        if rental_days <= 0 or rental_days > 90: 
            raise InvalidRentalDurationException()

        book = await BookService.get_book_by_id(session, book_id, lock_for_update=True) 

        if not book.is_available:
            raise BookNotAvailableException()

        overdue_queries = select(Rental).where(
            Rental.user_id == current_user.id,
            Rental.returned_at.is_(None),
            Rental.due_date < datetime.now(timezone.utc)
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


        due_date = datetime.now(timezone.utc) + timedelta(days=rental_days)
        total_price =  RentalService.calculate_rental_cost(rental_days)
        new_rent = Rental(user_id = current_user.id, book_id = book_id, due_date = due_date, total_price = total_price)
        session.add(new_rent)
        book.is_available = False 

        try:

            await session.commit()
            await session.refresh(new_rent)
            return new_rent 
        except Exception as e:
            await session.rollback()
            raise e

    
    @staticmethod
    def calculate_rental_cost(rental_days:int) -> float:
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
    async def return_book(session: AsyncSession, rental_id:int ,current_user: User, is_damaged: bool = False):
        query = select(Rental).where(Rental.id == rental_id)
        result = await session.execute(query)
        rental = result.scalar_one_or_none()

        if not rental:
            raise RentalNotFoundException()

        if not rental.user_id == current_user.id:
            raise PermissionDeniedException()
        
        if rental.returned_at:
            raise BookAlreadyReturnedException()

        rental.returned_at = datetime.now(timezone.utc)

        if rental.returned_at > rental.due_date:
            rental.total_price += min(2 * float(((rental.returned_at - rental.due_date).total_seconds()))/86_400,100)
        if is_damaged:
            rental.total_price += 15
        book = await BookService.get_book_by_id(session,rental.book_id)

        book.is_available = True 


        try:
            await session.commit()
            await session.refresh(rental)
            return rental
        except Exception as e:
            await session.rollback()
            raise e 

    @staticmethod
    async def get_user_rentals(session: AsyncSession, user_id:int, current_user:User):
        if current_user.id != user_id and not current_user.is_superuser:
            raise PermissionDeniedException()
        query = select(Rental).where(Rental.user_id==user_id)
        result = await session.execute(query)
        user_rentals = result.scalars().all()
        return user_rentals

    @staticmethod
    async def get_overdue_rentals(session: AsyncSession):
        query = select(Rental).where(
            Rental.due_date < datetime.now(timezone.utc),
            Rental.returned_at.is_(None)
        )
        result = await session.execute(query)

        return result.scalars().all()