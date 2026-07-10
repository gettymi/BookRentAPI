from fastapi import HTTPException, status


# ==========================================
# 1. Web Layer Exceptions 
# ==========================================

class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},)

class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )

# ==========================================
# 2. Service Layer Exceptions 
# ==========================================

class BaseServiceException(Exception):
    """Base class for all business logic exceptions."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class BookNotFoundException(BaseServiceException):
    def __init__(self, message="The requested book was not found in the database."):
        self.message = message
        super().__init__(message=self.message,status_code=status.HTTP_404_NOT_FOUND)  

class BookNotAvailableException(BaseServiceException):
    def __init__(self):
        super().__init__(message="This book is currently rented out.",status_code=status.HTTP_409_CONFLICT)

class TooLongRentalDaysException(BaseServiceException):
    def __init__(self, message="The number of rental's days are too big, max 365 days"):
        self.message = message
        super().__init__(message=self.message, status_code=status.HTTP_400_BAD_REQUEST)

class UserHasOverdueBooksException(BaseServiceException):
    def __init__(self, message="Please return your books to booked previously"):
        self.message=message
        super().__init__(message=self.message, status_code=status.HTTP_403_FORBIDDEN)

class RentalNotFoundException(BaseServiceException):
    def __init__(self, message="We were not able find your rental"):
        self.message = message
        super().__init__(message=self.message, status_code=status.HTTP_404_NOT_FOUND)
    
class BookAlreadyReturnedException(BaseServiceException):
        def __init__(self, message="Book is already returned"):
            self.message = message
            super().__init__(message=self.message, status_code=status.HTTP_409_CONFLICT)

class MaxRentalsReachedException(BaseServiceException):
        def __init__(self, message="Maximum number of books were rented"):
            self.message = message
            super().__init__(message=self.message, status_code=status.HTTP_403_FORBIDDEN)

class InvalidRentalDurationException(BaseServiceException):
        def __init__(self, message="Number of days provided is incorrect. limit 90"):
            self.message = message
            super().__init__(message=self.message, status_code=status.HTTP_400_BAD_REQUEST)