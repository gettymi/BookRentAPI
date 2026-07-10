from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_db 
from app.services.rental_service import RentalService
from app.models.rental import Rental
from app.schemas.rental import RentalCreate, RentalResponse
from app.core.dependencies import get_current_admin_user, get_current_user
from app.models.user import User

router = APIRouter()

@router.post('/',response_model=RentalResponse)
async def rent_book(book_id: int, rental_days: int, session:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await RentalService.rent_book(book_id=book_id,rental_days=rental_days,session=session,current_user=current_user)

@router.post('/{rental_id}/return', response_model=RentalResponse)
async def return_book(rental_id: int, is_damaged: bool = False, session:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await RentalService.return_book(rental_id=rental_id,is_damaged=is_damaged,session=session,current_user=current_user)

@router.get('/me', response_model=list[RentalResponse])
async def user_rents(session:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await RentalService.get_user_rentals(user_id=current_user.id, session=session, current_user=current_user)

@router.get('/overdue', response_model=list[RentalResponse])
async def overdue_rents (session:AsyncSession= Depends(get_db), current_admin_user: User = Depends(get_current_admin_user)):
    return await RentalService.get_overdue_rentals(session)