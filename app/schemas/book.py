from pydantic import BaseModel,ConfigDict

class BookBase(BaseModel):
    title: str
    author: str 
    price: float
    description:str | None = None

class BookCreate(BookBase):
    pass




class BookResponce(BookBase):
    id: int 
    
    model_config = ConfigDict(from_attributes=True)
