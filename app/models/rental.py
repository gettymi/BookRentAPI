from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime

class Rental(Base):
    __tablename__ = "rentals"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates = "rentals")
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    book: Mapped["Book"] = relationship(back_populates = "rentals")
    rented_at: Mapped[datetime] = mapped_column(default=func.now())
    due_date: Mapped[datetime] = mapped_column()
    returned_at: Mapped[datetime | None ] = mapped_column(default = None)
    status: Mapped[str] = mapped_column(String, default="active")
    total_price: Mapped[float] = mapped_column()