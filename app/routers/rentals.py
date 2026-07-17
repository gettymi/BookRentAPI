from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db 
from app.services.rental_service import RentalService
from app.models.rental import Rental
from app.schemas.rental import RentalCreate, RentalResponse
from app.schemas.pagination import PaginatedResponse
from app.core.dependencies import get_current_admin_user, get_current_user
from app.models.user import User

router = APIRouter()

@router.post('/',response_model=RentalResponse)
async def rent_book(
    book_id: int = Query(..., description="The ID of the book to rent", example=1),
    rental_days: int = Query(gt=0, le=90, description="The ID of the book to rent", example=14),
    session:AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Creates a new active rental for the current authenticated user.
    
    - **book_id**: The ID of the book to rent. Must be currently available.
    - **rental_days**: How long you want to keep the book (max 60 days).
    """
    
    return await RentalService.rent_book(book_id=book_id,rental_days=rental_days,session=session,current_user=current_user)

@router.post('/{rental_id}/return', response_model=RentalResponse)
async def return_book(rental_id: int, is_damaged: bool = False, session:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await RentalService.return_book(rental_id=rental_id,is_damaged=is_damaged,session=session,current_user=current_user)

@router.get('/me', response_model=PaginatedResponse[RentalResponse])
async def user_rents(status:str | None = None, end_date: datetime |None = None, start_date: datetime | None = None, size:int = 20, page:int = 1, session:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await RentalService.get_user_rentals(user_id=current_user.id,
     session=session,
     current_user=current_user,
     start_date=start_date, 
     status=status,
     end_date=end_date,
     size=size,
     page=page,
     )

@router.get('/overdue', response_model=list[RentalResponse])
async def overdue_rents (session:AsyncSession= Depends(get_db), current_admin_user: User = Depends(get_current_admin_user)):
    return await RentalService.get_overdue_rentals(session)