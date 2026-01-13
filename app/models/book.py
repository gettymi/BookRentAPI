from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Book(Base):
    __tablename__ = "books"
    id :Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), index=True)
    author: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column()
    is_available: Mapped[bool] = mapped_column(default=True)