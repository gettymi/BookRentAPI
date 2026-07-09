from pydantic import BaseModel, ConfigDict
from datetime import datetime

class RentalCreate(BaseModel):
    book_id: int
    rental_days: int

class RentalResponse(BaseModel):
    id:int
    user_id: int
    book_id: int
    rented_at: datetime
    due_date: datetime
    returned_at: datetime | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)
