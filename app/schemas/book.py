from pydantic import BaseModel,ConfigDict

class BookBase(BaseModel):
    title: str
    author: str 
    price: float
    year: int
    description:str | None = None


class BookCreate(BookBase):
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Clean Architecture",
                "author": "Robert C. Martin",
                "price": 34.99,
                "year": 2017,
                "description": "A Craftsman's Guide to Software Structure and Design."
            }
        }
    )


class BookResponse(BookBase):
    id: int 
    is_available: bool
    
    model_config = ConfigDict(from_attributes=True)


class BookUpdate(BaseModel):
    title:str | None = None
    author:str | None = None
    price:float | None= None
    year:int | None = None
    description:str | None = None
    is_available:bool | None = None

class BookCatalogResponse(BaseModel):
    title: str
    author: str
    year: int
    price: float
    book_id: int
    available_count: int 
