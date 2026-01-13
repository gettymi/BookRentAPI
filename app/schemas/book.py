from pydantic import BaseModel,ConfigDict

class BookBase(BaseModel):
    title: str
    author: str 
    price: float
    year: int
    description:str | None = None


class BookCreate(BookBase):
    pass


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