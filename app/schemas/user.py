from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
import re 

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)

    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "engineer@example.com",
                "password": "StrongPassword123!"
            }
        }
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, p:str) -> str:
        if not re.search(r"\d", p):
            raise ValueError("Password must contain at least one number")
        elif not re.search(r"[A-Z]", p):
            raise ValueError("Password must contain at least one uppercase letter")  
        return p

class UserResponse(UserBase):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None
    

    @field_validator("password")
    @classmethod
    def validate_password(cls, p:str) -> str | None:

        if p is None:
            return p

        if not re.search(r"\d", p):
            raise ValueError("Password must contain at least one number")
        elif not re.search(r"[A-Z]", p):
            raise ValueError("Password must contain at least one uppercase letter")  
        return p
